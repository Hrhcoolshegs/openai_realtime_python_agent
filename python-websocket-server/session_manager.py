"""
Session Management for Python WebSocket Server.

This module handles WebSocket connections and session state management
between Twilio calls, OpenAI Realtime API, and the frontend.

Converted from TypeScript sessionManager.ts to Python with async/await patterns.
"""

import json
import logging
import asyncio
import websockets
from typing import Optional, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect

from models import Session, FunctionCallItem
from function_handlers import handle_function_call
from utils import (
    parse_message, 
    json_send, 
    is_websocket_open, 
    cleanup_websocket,
    create_twilio_media_message,
    create_openai_audio_message,
    format_function_call_response
)


logger = logging.getLogger(__name__)

# Global session instance (converted from TypeScript module-level session)
session = Session()


class SessionManager:
    """
    Manages WebSocket connections and message routing.
    
    Converted from TypeScript function-based approach to Python class-based approach
    for better state management and error handling.
    """
    
    def __init__(self):
        self.session = session
    
    async def handle_call_connection(self, websocket: WebSocket, openai_api_key: str):
        """
        Handle incoming Twilio call WebSocket connection.
        
        Converted from TypeScript handleCallConnection function.
        
        Args:
            websocket: FastAPI WebSocket connection from Twilio
            openai_api_key: OpenAI API key for Realtime API
        """
        # Cleanup existing connection
        await cleanup_websocket(self.session.twilio_conn)
        
        # Accept the new connection
        await websocket.accept()
        self.session.twilio_conn = websocket
        self.session.openai_api_key = openai_api_key
        
        try:
            while True:
                # Receive message from Twilio
                data = await websocket.receive_text()
                await self._handle_twilio_message(data)
                
        except WebSocketDisconnect:
            logger.info("Twilio WebSocket disconnected")
        except Exception as e:
            logger.error(f"Error in Twilio connection: {e}")
        finally:
            # Cleanup on connection close
            await self._cleanup_call_connection()
    
    async def handle_frontend_connection(self, websocket: WebSocket):
        """
        Handle incoming frontend WebSocket connection.
        
        Converted from TypeScript handleFrontendConnection function.
        
        Args:
            websocket: FastAPI WebSocket connection from frontend
        """
        # Cleanup existing connection
        await cleanup_websocket(self.session.frontend_conn)
        
        # Accept the new connection
        await websocket.accept()
        self.session.frontend_conn = websocket
        
        try:
            while True:
                # Receive message from frontend
                data = await websocket.receive_text()
                await self._handle_frontend_message(data)
                
        except WebSocketDisconnect:
            logger.info("Frontend WebSocket disconnected")
        except Exception as e:
            logger.error(f"Error in frontend connection: {e}")
        finally:
            # Cleanup on connection close
            await cleanup_websocket(self.session.frontend_conn)
            self.session.frontend_conn = None
            
            # Clear session if no other connections
            if not self.session.twilio_conn and not self.session.model_conn:
                self._reset_session()
    
    async def _handle_twilio_message(self, data: str):
        """
        Handle messages from Twilio WebSocket.
        
        FIXED: Proper timestamp handling
        """
        msg = parse_message(data)
        if not msg:
            return
        
        event = msg.get("event")
        
        if event == "start":
            # Call started - initialize session
            start_data = msg.get("start", {})
            self.session.stream_sid = start_data.get("streamSid")
            self.session.latest_media_timestamp = 0  # Initialize as int
            self.session.last_assistant_item = None
            self.session.response_start_timestamp = None
            
            # Try to connect to OpenAI
            await self._try_connect_model()
            
        elif event == "media":
            # Audio data from Twilio - FIXED: Convert timestamp to int
            media_data = msg.get("media", {})
            try:
                self.session.latest_media_timestamp = int(media_data.get("timestamp", 0))
            except (ValueError, TypeError):
                self.session.latest_media_timestamp = 0
            
            # Forward audio to OpenAI if connected
            if self._is_model_connected():
                audio_message = create_openai_audio_message(media_data.get("payload", ""))
                await self._send_to_model(audio_message)
                
        elif event == "close":
            # Call ended
            logger.info("Twilio call ended")
            await self._close_all_connections()
    
    async def _handle_frontend_message(self, data: str):
        """
        Handle messages from frontend WebSocket.
        
        Converted from TypeScript handleFrontendMessage function.
        
        Args:
            data: Raw message data from frontend
        """
        msg = parse_message(data)
        if not msg:
            return
        
        # Forward to OpenAI model if connected
        if self._is_model_connected():
            await self._send_to_model(msg)
        
        # Save session configuration
        if msg.get("type") == "session.update":
            self.session.saved_config = msg.get("session", {})
    
    async def _try_connect_model(self):
        """
        Attempt to connect to OpenAI Realtime API.
        
        Converted from TypeScript tryConnectModel function.
        """
        if not all([
            self.session.twilio_conn,
            self.session.stream_sid,
            self.session.openai_api_key
        ]):
            logger.warning("Cannot connect to model: missing required session data")
            return
        
        if self._is_model_connected():
            logger.info("Model already connected")
            return
        
        try:
            # Connect to OpenAI Realtime API
            headers = {
                "Authorization": f"Bearer {self.session.openai_api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            uri = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
            
            # Create WebSocket connection
            self.session.model_conn = await websockets.connect(
                    uri, 
                    extra_headers=headers,
                    ping_interval=20,      # Send ping every 20 seconds  
                    ping_timeout=10,       # Wait 10 seconds for pong response
                    close_timeout=10,      # Wait 10 seconds for close handshake
                    max_size=10**7,        # Increase max message size for audio
                    max_queue=32           # Increase message queue size
                )
            
            # Start listening for messages in background
            asyncio.create_task(self._handle_model_messages())
            
            # Send initial configuration
            await self._send_initial_config()
            
            logger.info("Connected to OpenAI Realtime API")
            
        except Exception as e:
            logger.error(f"Failed to connect to OpenAI: {e}")
            self.session.model_conn = None
    
    async def _send_initial_config(self):
        """
        Send initial configuration to OpenAI Realtime API.
        
        Converted from TypeScript session.update message in tryConnectModel.
        """
        config = self.session.saved_config or {}
        
        default_config = {
            "modalities": ["text", "audio"],
            "turn_detection": {"type": "server_vad"},
            "voice": "ash",
            "input_audio_transcription": {"model": "whisper-1"},
            "input_audio_format": "g711_ulaw",
            "output_audio_format": "g711_ulaw"
        }
        
        # Merge with saved config
        final_config = {**default_config, **config}
        
        session_update = {
            "type": "session.update",
            "session": final_config
        }
        
        await self._send_to_model(session_update)
    
    async def _handle_model_messages(self):
        """
        Handle messages from OpenAI Realtime API.
        
        FIXED: Proper exception handling to distinguish between normal closure and errors
        """
        try:
            async for message in self.session.model_conn:
                await self._process_model_message(message)
                
        except websockets.exceptions.ConnectionClosed as e:
            logger.info(f"OpenAI WebSocket connection closed normally: {e}")
            
        except websockets.exceptions.ConnectionClosedError as e:
            logger.warning(f"OpenAI WebSocket connection closed with error: {e}")
            
        except Exception as e:
            logger.error(f"Error handling model messages: {e}")
            
        finally:
            await self._close_model()
    
    async def _process_model_message(self, data: str):
        """
        Process individual message from OpenAI model.
        
        Args:
            data: Raw message from OpenAI
        """
        event = parse_message(data)
        if not event:
            return
        
        # Forward to frontend
        if self.session.frontend_conn:
            await json_send(self.session.frontend_conn, event)
        
        event_type = event.get("type")
        
        if event_type == "input_audio_buffer.speech_started":
            await self._handle_truncation()
            
        elif event_type == "response.audio.delta":
            await self._handle_audio_delta(event)
            
        elif event_type == "response.output_item.done":
            await self._handle_output_item_done(event)
    
    async def _handle_audio_delta(self, event: Dict[str, Any]):
        """
        Handle audio delta from OpenAI (streaming audio response).
        
        FIXED: Proper timestamp handling
        """
        if not (self.session.twilio_conn and self.session.stream_sid):
            return
        
        # Track response timing - FIXED: Convert timestamp to int
        if self.session.response_start_timestamp is None:
            try:
                self.session.response_start_timestamp = int(self.session.latest_media_timestamp or 0)
            except (ValueError, TypeError):
                self.session.response_start_timestamp = 0
        
        if event.get("item_id"):
            self.session.last_assistant_item = event["item_id"]
        
        # Send audio to Twilio
        audio_payload = event.get("delta", "")
        if audio_payload:
            media_message = create_twilio_media_message(
                self.session.stream_sid, 
                audio_payload
            )
            await json_send(self.session.twilio_conn, media_message)
            
            # Send mark message
            mark_message = {
                "event": "mark",
                "streamSid": self.session.stream_sid
            }
            await json_send(self.session.twilio_conn, mark_message)
    
    async def _handle_output_item_done(self, event: Dict[str, Any]):
        """
        Handle completed output item from OpenAI.
        
        Converted from TypeScript response.output_item.done case.
        
        Args:
            event: Output item done event from OpenAI
        """
        item = event.get("item", {})
        
        if item.get("type") == "function_call":
            try:
                # Handle function call
                function_name = item.get("name", "")
                function_args = item.get("arguments", "{}")
                call_id = item.get("call_id", "")
                
                # Execute function
                result = await handle_function_call(function_name, function_args)
                
                # Send result back to OpenAI
                if self._is_model_connected():
                    response_message = {
                        "type": "conversation.item.create",
                        "item": {
                            "type": "function_call_output",
                            "call_id": call_id,
                            "output": result
                        }
                    }
                    await self._send_to_model(response_message)
                    
                    # Trigger response generation
                    await self._send_to_model({"type": "response.create"})
                    
            except Exception as e:
                logger.error(f"Error handling function call: {e}")
    
    async def _handle_truncation(self):
        """
        Handle audio truncation when user starts speaking.
        
        FIXED: Proper timestamp handling with type conversion
        """
        if (not self.session.last_assistant_item or 
            self.session.response_start_timestamp is None):
            return
        
        # Calculate elapsed time - FIXED: Convert to int/float for math operations
        try:
            latest_timestamp = int(self.session.latest_media_timestamp or 0)
            response_start = int(self.session.response_start_timestamp or 0)
            elapsed_ms = latest_timestamp - response_start
            audio_end_ms = max(elapsed_ms, 0)
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid timestamp values, using 0: {e}")
            audio_end_ms = 0
        
        # Send truncation to OpenAI
        if self._is_model_connected():
            truncate_message = {
                "type": "conversation.item.truncate",
                "item_id": self.session.last_assistant_item,
                "content_index": 0,
                "audio_end_ms": audio_end_ms
            }
            await self._send_to_model(truncate_message)
        
        # Clear Twilio audio buffer
        if self.session.twilio_conn and self.session.stream_sid:
            clear_message = {
                "event": "clear",
                "streamSid": self.session.stream_sid
            }
            await json_send(self.session.twilio_conn, clear_message)
        
        # Reset tracking variables
        self.session.last_assistant_item = None
        self.session.response_start_timestamp = None
    
    async def _send_to_model(self, message: Dict[str, Any]):
        """
        Send message to OpenAI model WebSocket.
        
        Args:
            message: Message to send to OpenAI
        """
        if self._is_model_connected():
            try:
                json_data = json.dumps(message)
                await self.session.model_conn.send(json_data)
            except Exception as e:
                logger.error(f"Failed to send to model: {e}")
    
    def _is_model_connected(self) -> bool:
        """
        Check if OpenAI model connection is active.
        
        Returns:
            True if model is connected
        """
        return (self.session.model_conn is not None and 
                not self.session.model_conn.closed)
    
    async def _close_model(self):
        """
        Close OpenAI model connection and cleanup.
        
        Converted from TypeScript closeModel function.
        """
        if self.session.model_conn:
            try:
                await self.session.model_conn.close()
            except Exception as e:
                logger.error(f"Error closing model connection: {e}")
        
        self.session.model_conn = None
        
        # Clear session if no other connections
        if not self.session.twilio_conn and not self.session.frontend_conn:
            self._reset_session()
    
    async def _close_all_connections(self):
        """
        Close all WebSocket connections and reset session.
        
        Converted from TypeScript closeAllConnections function.
        """
        # Close Twilio connection
        await cleanup_websocket(self.session.twilio_conn)
        self.session.twilio_conn = None
        
        # Close model connection
        if self.session.model_conn:
            try:
                await self.session.model_conn.close()
            except:
                pass
        self.session.model_conn = None
        
        # Close frontend connection
        await cleanup_websocket(self.session.frontend_conn)
        self.session.frontend_conn = None
        
        # Reset session data
        self._reset_session()
    
    async def _cleanup_call_connection(self):
        """
        Cleanup when Twilio call connection closes.
        """
        await cleanup_websocket(self.session.model_conn)
        await cleanup_websocket(self.session.twilio_conn)
        
        self.session.twilio_conn = None
        self.session.model_conn = None
        self.session.stream_sid = None
        self.session.last_assistant_item = None
        self.session.response_start_timestamp = None
        self.session.latest_media_timestamp = None
        
        # Keep session if frontend is still connected
        if not self.session.frontend_conn:
            self._reset_session()
    
    def _reset_session(self):
        """
        Reset session to initial state.
        """
        global session
        session = Session()
        self.session = session


# Global session manager instance
session_manager = SessionManager()


# Public functions for use by main server (converted from TypeScript exports)
async def handle_call_connection(websocket: WebSocket, openai_api_key: str):
    """
    Public function to handle Twilio call connections.
    
    Args:
        websocket: FastAPI WebSocket connection
        openai_api_key: OpenAI API key
    """
    await session_manager.handle_call_connection(websocket, openai_api_key)


async def handle_frontend_connection(websocket: WebSocket):
    """
    Public function to handle frontend connections.
    
    Args:
        websocket: FastAPI WebSocket connection
    """
    await session_manager.handle_frontend_connection(websocket)

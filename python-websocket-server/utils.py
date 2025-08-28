"""
Utility functions for the Python WebSocket Server.

This module contains helper functions for WebSocket handling, JSON operations,
and other common tasks. Converted from various utility functions scattered
throughout the TypeScript codebase.
"""

import json
import logging
from typing import Optional, Dict, Any, Union
from fastapi import WebSocket, WebSocketDisconnect


logger = logging.getLogger(__name__)


def parse_message(data: Union[str, bytes]) -> Optional[Dict[str, Any]]:
    """
    Parse incoming WebSocket message data.
    
    Converted from TypeScript parseMessage function.
    Handles both string and bytes input, safely parsing JSON.
    
    Args:
        data: Raw WebSocket message data
        
    Returns:
        Parsed JSON as dictionary, or None if parsing fails
    """
    try:
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        
        return json.loads(data)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logger.error(f"Failed to parse message: {e}")
        return None


async def json_send(websocket: WebSocket, data: Dict[str, Any]) -> bool:
    """
    Send JSON data over WebSocket connection.
    
    Converted from TypeScript jsonSend function.
    Safely serializes and sends JSON data.
    
    Args:
        websocket: FastAPI WebSocket connection
        data: Data to send as JSON
        
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        json_data = json.dumps(data)
        await websocket.send_text(json_data)
        return True
    except (WebSocketDisconnect, Exception) as e:
        logger.error(f"Failed to send JSON message: {e}")
        return False


def is_websocket_open(websocket: Optional[WebSocket]) -> bool:
    """
    Check if WebSocket connection is open and ready.
    
    Converted from TypeScript isOpen function.
    
    Args:
        websocket: WebSocket connection to check
        
    Returns:
        True if connection is open, False otherwise
    """
    if websocket is None:
        return False
    
    try:
        # In FastAPI, we check the client_state
        return websocket.client_state.name == "CONNECTED"
    except AttributeError:
        # Fallback check
        return websocket is not None


async def cleanup_websocket(websocket: Optional[WebSocket]) -> None:
    """
    Safely close and cleanup a WebSocket connection.
    
    Converted from TypeScript cleanupConnection function.
    
    Args:
        websocket: WebSocket connection to cleanup
    """
    if websocket is None:
        return
    
    try:
        if is_websocket_open(websocket):
            await websocket.close()
    except Exception as e:
        logger.error(f"Error during WebSocket cleanup: {e}")


def create_twilio_media_message(stream_sid: str, audio_payload: str) -> Dict[str, Any]:
    """
    Create a Twilio media message structure.
    
    Helper function to create properly formatted Twilio WebSocket messages.
    
    Args:
        stream_sid: Twilio stream session ID
        audio_payload: Base64 encoded audio data
        
    Returns:
        Formatted Twilio message dictionary
    """
    return {
        "event": "media",
        "streamSid": stream_sid,
        "media": {
            "payload": audio_payload
        }
    }


def create_openai_audio_message(audio_data: str) -> Dict[str, Any]:
    """
    Create an OpenAI Realtime API audio input message.
    
    Helper function to create properly formatted OpenAI API messages.
    
    Args:
        audio_data: Base64 encoded audio data
        
    Returns:
        Formatted OpenAI message dictionary
    """
    return {
        "type": "input_audio_buffer.append",
        "audio": audio_data
    }


def extract_audio_from_openai_response(response: Dict[str, Any]) -> Optional[str]:
    """
    Extract audio data from OpenAI Realtime API response.
    
    Helper function to parse audio content from OpenAI responses.
    
    Args:
        response: OpenAI API response dictionary
        
    Returns:
        Base64 encoded audio data or None if not found
    """
    try:
        if response.get("type") == "response.audio.delta":
            return response.get("delta")
        elif response.get("type") == "response.audio":
            return response.get("audio")
        return None
    except (KeyError, AttributeError):
        return None


def format_function_call_response(call_id: str, result: str) -> Dict[str, Any]:
    """
    Format a function call response for OpenAI Realtime API.
    
    Args:
        call_id: Function call ID from OpenAI
        result: Function execution result
        
    Returns:
        Formatted response dictionary
    """
    return {
        "type": "conversation.item.create",
        "item": {
            "type": "function_call_output",
            "call_id": call_id,
            "output": result
        }
    }


class ConnectionError(Exception):
    """Custom exception for WebSocket connection errors"""
    pass


class MessageParsingError(Exception):
    """Custom exception for message parsing errors"""
    pass

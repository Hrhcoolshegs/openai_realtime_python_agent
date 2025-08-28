"""
Type definitions for the Python WebSocket Server

This module defines the data structures used throughout the application.
Converted from TypeScript interfaces to Python dataclasses and Pydantic models.

Original TypeScript types.ts equivalent.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pydantic import BaseModel
from fastapi import WebSocket


@dataclass
class Session:
    """
    Session data structure to maintain connection state.
    
    Converted from TypeScript Session interface.
    Holds references to active WebSocket connections and session data.
    """
    twilio_conn: Optional[WebSocket] = None
    frontend_conn: Optional[WebSocket] = None
    model_conn: Optional[WebSocket] = None
    stream_sid: Optional[str] = None
    saved_config: Optional[Dict[str, Any]] = None
    last_assistant_item: Optional[str] = None
    response_start_timestamp: Optional[int] = None
    latest_media_timestamp: Optional[int] = None
    openai_api_key: Optional[str] = None


class FunctionCallItem(BaseModel):
    """
    Pydantic model for function call items from OpenAI.
    
    Converted from TypeScript FunctionCallItem interface.
    Used for parsing function calls from the OpenAI Realtime API.
    """
    name: str
    arguments: str
    call_id: Optional[str] = None


class FunctionParameter(BaseModel):
    """
    Schema for function parameters.
    
    Defines the structure of function parameters in OpenAI function schemas.
    """
    type: str
    description: Optional[str] = None


class FunctionSchema(BaseModel):
    """
    Schema definition for OpenAI function calling.
    
    Converted from TypeScript FunctionSchema interface.
    Defines the structure that OpenAI expects for function definitions.
    """
    name: str
    type: str = "function"
    description: Optional[str] = None
    parameters: Dict[str, Any]


class FunctionHandler(BaseModel):
    """
    Function handler with schema and implementation.
    
    Converted from TypeScript FunctionHandler interface.
    Combines the OpenAI schema with the actual Python function implementation.
    """
    schema: FunctionSchema
    
    class Config:
        arbitrary_types_allowed = True  # Allow callable types


# Twilio WebSocket message types
class TwilioStartMessage(BaseModel):
    """Twilio WebSocket start message structure"""
    event: str = "start"
    start: Dict[str, Any]


class TwilioMediaMessage(BaseModel):
    """Twilio WebSocket media message structure"""
    event: str = "media"
    media: Dict[str, Any]


class TwilioCloseMessage(BaseModel):
    """Twilio WebSocket close message structure"""
    event: str = "close"


# OpenAI Realtime API message types
class OpenAIInputAudioMessage(BaseModel):
    """OpenAI input audio buffer message"""
    type: str = "input_audio_buffer.append"
    audio: str


class OpenAIResponseMessage(BaseModel):
    """OpenAI response message structure"""
    type: str
    response: Optional[Dict[str, Any]] = None


# Frontend WebSocket message types
class FrontendConfigMessage(BaseModel):
    """Frontend configuration message"""
    type: str = "configure"
    config: Dict[str, Any]


class ToolListResponse(BaseModel):
    """Response model for /tools endpoint"""
    tools: List[FunctionSchema]


class PublicUrlResponse(BaseModel):
    """Response model for /public-url endpoint"""
    public_url: str


# Error response models
class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None

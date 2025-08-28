"""
Main FastAPI Server for Twilio OpenAI Realtime Demo.

This is the main entry point for the Python WebSocket server.
Converted from TypeScript server.ts to Python FastAPI.

Key conversions:
- Express.js → FastAPI
- Node.js HTTP server → uvicorn ASGI server  
- ws WebSocketServer → FastAPI WebSocket endpoints
- File operations → pathlib/open()
- Environment variables → python-dotenv
"""

import os
import logging
from pathlib import Path
from urllib.parse import urlparse, urlunparse
from typing import Dict, Any

from fastapi import FastAPI, WebSocket, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import uvicorn
from dotenv import load_dotenv

from session_manager import handle_call_connection, handle_frontend_connection
from function_handlers import get_function_schemas
from models import ToolListResponse, PublicUrlResponse, ErrorResponse


# Load environment variables
load_dotenv()

# Configuration (converted from TypeScript process.env access)
PORT = int(os.getenv("PORT", "8081"))
HOST = os.getenv("HOST", "0.0.0.0")
PUBLIC_URL = os.getenv("PUBLIC_URL", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Validate required environment variables
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

if not PUBLIC_URL:
    print("Warning: PUBLIC_URL not set. TwiML webhook may not work correctly.")

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app (equivalent to Express.js app)
app = FastAPI(
    title="Twilio OpenAI Realtime WebSocket Server",
    description="Python FastAPI server for handling Twilio calls with OpenAI Realtime API",
    version="1.0.0"
)

# Add CORS middleware (equivalent to Express cors())
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load TwiML template (converted from fs.readFileSync)
TWIML_PATH = Path(__file__).parent / "twiml.xml"
try:
    with open(TWIML_PATH, "r", encoding="utf-8") as f:
        TWIML_TEMPLATE = f.read()
except FileNotFoundError:
    logger.error(f"TwiML template not found at {TWIML_PATH}")
    TWIML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say>Connected</Say>
  <Connect>
    <Stream url="{{WS_URL}}" />
  </Connect>
  <Say>Disconnected</Say>
</Response>"""


@app.get("/", response_class=PlainTextResponse)
async def health_check():
    """
    Health check endpoint.
    
    New endpoint not in original TypeScript version.
    Useful for monitoring and deployment health checks.
    """
    return "Python WebSocket Server is running"


@app.get("/public-url")
async def get_public_url():
    """
    Get the public URL for this server.
    
    FIXED: Return format that matches frontend expectations
    """
    return {"publicUrl": PUBLIC_URL} 


@app.api_route("/twiml", methods=["GET", "POST"])      # ADD THIS LINE
@app.api_route("//twiml", methods=["GET", "POST"])     # KEEP THIS LINE
async def get_twiml(request: Request):
    """
    Generate TwiML response for Twilio webhook.
    
    FIXED: Ensure both GET and POST work properly for frontend checks
    """
    if not PUBLIC_URL:
        # Don't raise error for frontend checks - return empty response
        logger.warning("PUBLIC_URL not configured")
        return Response(
            content="<?xml version='1.0' encoding='UTF-8'?><Response><Say>Not configured</Say></Response>",
            media_type="application/xml"
        )
    
    try:
        # Parse and modify URL for WebSocket
        parsed_url = urlparse(PUBLIC_URL.rstrip('/'))
        
        # Change protocol to WebSocket and set path
        ws_url = urlunparse((
            "wss" if parsed_url.scheme == "https" else "ws",
            parsed_url.netloc,
            "/call",
            "",
            "",
            ""
        ))
        
        # Replace placeholder in template
        twiml_content = TWIML_TEMPLATE.replace("{{WS_URL}}", ws_url)
        
        logger.info(f"Generated TwiML with WebSocket URL: {ws_url}")
        
        return Response(
            content=twiml_content, 
            media_type="application/xml"
        )
        
    except Exception as e:
        logger.error(f"Error generating TwiML: {e}")
        return Response(
            content="<?xml version='1.0' encoding='UTF-8'?><Response><Say>Error</Say></Response>",
            media_type="application/xml"
        )

@app.get("/tools")  # Remove response_model=ToolListResponse
async def get_tools():
    """
    Get available function schemas for OpenAI function calling.
    
    Returns direct array to match frontend expectations.
    """
    try:
        schemas = get_function_schemas()
        return schemas  # Return direct array, not wrapped in ToolListResponse
    except Exception as e:
        logger.error(f"Error getting tools: {e}")
        return []  # Return empty array on error instead of raising exception


@app.websocket("/call")
async def websocket_call_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for Twilio call connections.
    
    Converted from WebSocketServer connection handling in TypeScript:
    if (type === "call") { handleCallConnection(currentCall, OPENAI_API_KEY); }
    
    This endpoint receives the audio stream from Twilio and forwards it
    to the OpenAI Realtime API.
    """
    logger.info("New Twilio call WebSocket connection")
    try:
        await handle_call_connection(websocket, OPENAI_API_KEY)
    except Exception as e:
        logger.error(f"Error in call WebSocket: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass


@app.websocket("/logs")
async def websocket_logs_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for frontend logging connections.
    
    Converted from WebSocketServer connection handling in TypeScript:
    if (type === "logs") { handleFrontendConnection(currentLogs); }
    
    This endpoint allows the frontend webapp to receive real-time
    updates about the call session and AI responses.
    """
    logger.info("New frontend logs WebSocket connection")
    try:
        await handle_frontend_connection(websocket)
    except Exception as e:
        logger.error(f"Error in logs WebSocket: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    
    Provides better error handling than the original TypeScript version.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return Response(
        content=f"Internal Server Error: {str(exc)}", 
        status_code=500
    )


def main():
    """
    Main entry point for the application.
    
    Converted from TypeScript:
    server.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`))
    """
    logger.info(f"Starting server on {HOST}:{PORT}")
    logger.info(f"Public URL: {PUBLIC_URL}")
    logger.info(f"OpenAI API Key configured: {'Yes' if OPENAI_API_KEY else 'No'}")
    
    # Run the FastAPI server with uvicorn (equivalent to http.createServer + server.listen)
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        log_level=LOG_LEVEL.lower(),
        reload=False,  # Set to True for development
        access_log=True
    )


if __name__ == "__main__":
    main()


"""
Deployment Notes:

1. Development:
   python main.py
   
2. Production with Gunicorn:
   pip install gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8081

3. Docker:
   FROM python:3.11-slim
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["python", "main.py"]

4. Environment Variables:
   - OPENAI_API_KEY: Required
   - PUBLIC_URL: Required for Twilio webhook
   - PORT: Optional, defaults to 8081
   - HOST: Optional, defaults to 0.0.0.0
   - LOG_LEVEL: Optional, defaults to INFO
"""

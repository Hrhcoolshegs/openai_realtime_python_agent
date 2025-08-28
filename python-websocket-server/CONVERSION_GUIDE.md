# TypeScript to Python Conversion Guide

This document provides a detailed comparison of the original TypeScript/Node.js websocket-server and the new Python implementation.

## 📁 File Structure Comparison

### Original TypeScript Structure
```
websocket-server/
├── package.json
├── tsconfig.json
├── .env
├── src/
│   ├── server.ts
│   ├── sessionManager.ts
│   ├── functionHandlers.ts
│   ├── types.ts
│   └── twiml.xml
```

### New Python Structure
```
python-websocket-server/
├── requirements.txt
├── .env
├── main.py (server.ts)
├── session_manager.py (sessionManager.ts)
├── function_handlers.py (functionHandlers.ts)
├── types.py (types.ts)
├── utils.py (new utilities)
├── start.py (startup script)
├── twiml.xml
├── README.md
└── QUICKSTART.md
```

## 🔄 Technology Stack Conversion

| TypeScript/Node.js | Python Equivalent | Notes |
|-------------------|------------------|-------|
| Express.js | FastAPI | Modern async web framework |
| ws library | FastAPI WebSockets + websockets | Native WebSocket support |
| http.createServer() | uvicorn | ASGI server |
| dotenv | python-dotenv | Environment variables |
| fs.readFileSync | pathlib/open() | File operations |
| JSON.parse/stringify | json.loads/dumps | JSON handling |
| fetch() | httpx | HTTP client |
| TypeScript interfaces | Pydantic models | Type validation |
| Promise/async-await | async/await | Native async support |

## 📝 Code Conversion Examples

### 1. Server Setup

**TypeScript (server.ts):**
```typescript
import express from "express";
import { WebSocketServer } from "ws";
import http from "http";
import cors from "cors";

const app = express();
app.use(cors());
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

server.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
```

**Python (main.py):**
```python
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])

@app.websocket("/call")
async def websocket_endpoint(websocket: WebSocket):
    await handle_call_connection(websocket, OPENAI_API_KEY)

uvicorn.run(app, host="0.0.0.0", port=8081)
```

### 2. WebSocket Message Handling

**TypeScript:**
```typescript
function handleTwilioMessage(data: RawData) {
  const msg = parseMessage(data);
  if (!msg) return;

  switch (msg.event) {
    case "start":
      session.streamSid = msg.start.streamSid;
      tryConnectModel();
      break;
    case "media":
      if (isOpen(session.modelConn)) {
        jsonSend(session.modelConn, {
          type: "input_audio_buffer.append",
          audio: msg.media.payload,
        });
      }
      break;
  }
}
```

**Python:**
```python
async def _handle_twilio_message(self, data: str):
    msg = parse_message(data)
    if not msg:
        return

    event = msg.get("event")
    
    if event == "start":
        start_data = msg.get("start", {})
        self.session.stream_sid = start_data.get("streamSid")
        await self._try_connect_model()
        
    elif event == "media":
        if self._is_model_connected():
            audio_message = create_openai_audio_message(
                msg.get("media", {}).get("payload", "")
            )
            await self._send_to_model(audio_message)
```

### 3. Function Calling

**TypeScript:**
```typescript
const functions: FunctionHandler[] = [];

functions.push({
  schema: {
    name: "get_weather_from_coords",
    type: "function",
    parameters: { /* ... */ },
  },
  handler: async (args: { latitude: number; longitude: number }) => {
    const response = await fetch(`https://api.open-meteo.com/...`);
    const data = await response.json();
    return JSON.stringify({ temp: data.current?.temperature_2m });
  },
});
```

**Python:**
```python
async def get_weather_from_coords(latitude: float, longitude: float) -> str:
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}..."
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        
    current_temp = data.get("current", {}).get("temperature_2m")
    return json.dumps({"temp": current_temp})

class FunctionRegistry:
    def __init__(self):
        self._functions = {}
        self.register_function(WEATHER_SCHEMA, get_weather_from_coords)
```

### 4. Type Definitions

**TypeScript (types.ts):**
```typescript
export interface Session {
  twilioConn?: WebSocket;
  frontendConn?: WebSocket;
  modelConn?: WebSocket;
  streamSid?: string;
}

export interface FunctionSchema {
  name: string;
  type: "function";
  parameters: Record<string, any>;
}
```

**Python (types.py):**
```python
from dataclasses import dataclass
from pydantic import BaseModel
from typing import Optional, Dict, Any

@dataclass
class Session:
    twilio_conn: Optional[WebSocket] = None
    frontend_conn: Optional[WebSocket] = None
    model_conn: Optional[WebSocket] = None
    stream_sid: Optional[str] = None

class FunctionSchema(BaseModel):
    name: str
    type: str = "function"
    parameters: Dict[str, Any]
```

## 🚀 Key Improvements in Python Version

### 1. **Better Type Safety**
- Pydantic models for request/response validation
- Full type hints throughout the codebase
- Runtime type checking

### 2. **Enhanced Error Handling**
- Structured exception handling
- Detailed logging with Python logging module
- Graceful degradation on errors

### 3. **Modern Python Patterns**
- Context managers for resource cleanup
- Async/await throughout
- Class-based organization

### 4. **Better Development Experience**
- Auto-generated API documentation (FastAPI)
- Better IDE support with type hints
- Easier testing with pytest

### 5. **Production Ready Features**
- Health check endpoints
- Configurable logging levels
- Environment-based configuration
- Docker-friendly structure

## 🔧 Environment Configuration

### TypeScript (.env):
```
OPENAI_API_KEY="sk-..."
PUBLIC_URL="https://abc.ngrok-free.app"
```

### Python (.env):
```
OPENAI_API_KEY="sk-..."
PUBLIC_URL="https://abc.ngrok-free.app"
PORT=8081
HOST=0.0.0.0
LOG_LEVEL=INFO
```

## 📦 Dependencies Comparison

### TypeScript (package.json):
```json
{
  "dependencies": {
    "express": "^4.21.2",
    "ws": "^8.18.0",
    "dotenv": "^16.4.5",
    "cors": "^2.8.5",
    "ts-node": "^10.9.2",
    "typescript": "^5.5.4"
  }
}
```

### Python (requirements.txt):
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
python-dotenv==1.0.0
httpx==0.25.2
pydantic==2.5.1
```

## 🏃‍♂️ Running the Servers

### TypeScript:
```bash
cd websocket-server
npm install
npm run dev
```

### Python:
```bash
cd python-websocket-server
pip install -r requirements.txt
python start.py
# OR
python main.py
# OR
uvicorn main:app --reload
```

## 🧪 Testing

### TypeScript:
- Manual testing with WebSocket clients
- Basic error handling

### Python:
- FastAPI automatic OpenAPI docs at `/docs`
- Health check endpoint `/`
- Better error responses
- Structured logging

## 🌐 Deployment

### TypeScript:
```bash
npm run build
node dist/server.js
```

### Python:
```bash
# Development
python main.py

# Production
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Docker
docker build -t python-websocket-server .
docker run -p 8081:8081 python-websocket-server
```

## 📊 Performance Considerations

1. **FastAPI vs Express**: FastAPI generally has better performance for async operations
2. **WebSocket Handling**: Both implementations are comparable
3. **Memory Usage**: Python may use slightly more memory but offers better garbage collection
4. **Scalability**: Both can be scaled horizontally, Python offers more deployment options

## 🔀 Migration Path

To migrate from the TypeScript version:

1. **Keep the frontend unchanged** - it connects to the same WebSocket endpoints
2. **Update ngrok URL** - point to the Python server instead
3. **Copy environment variables** - from TypeScript .env to Python .env
4. **Test function calling** - ensure all custom functions work correctly
5. **Update Twilio webhook** - point to the new Python server TwiML endpoint

## 🎯 Use Cases for Each Version

### Choose TypeScript when:
- Team is primarily JavaScript/TypeScript focused
- Tight integration with Node.js ecosystem required
- Minimal dependencies preferred

### Choose Python when:
- Team has Python expertise
- Integration with AI/ML libraries needed (LangGraph, etc.)
- Better type safety and validation required
- Production deployment flexibility needed
- Auto-documentation is valuable

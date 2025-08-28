# Python WebSocket Server - Twilio OpenAI Realtime Demo

This is a complete Python conversion of the original TypeScript/Node.js websocket-server. This FastAPI-based server handles real-time voice communication between Twilio phone calls and OpenAI's Realtime API.

## 🔄 Conversion Overview

### JavaScript/TypeScript → Python Equivalents

| Original Technology | Python Equivalent | Purpose |
|-------------------|------------------|---------|
| Express.js | FastAPI | Web server framework |
| ws (WebSocket) | FastAPI WebSockets | WebSocket handling |
| http module | uvicorn | HTTP server |
| dotenv | python-dotenv | Environment variables |
| fs.readFileSync | pathlib/open() | File operations |
| JSON.parse/stringify | json module | JSON handling |

### Architecture Changes

1. **Express Routes → FastAPI Endpoints**
   - `/twiml` → FastAPI route with XML response
   - `/tools` → FastAPI route returning JSON
   - `/public-url` → FastAPI route returning JSON

2. **WebSocket Server → FastAPI WebSockets**
   - Node.js WebSocketServer → FastAPI WebSocket endpoints
   - Connection handling via dependency injection

3. **Module System → Python Packages**
   - TypeScript imports → Python imports
   - ES6 modules → Python modules

## 🏗️ File Structure

```
python-websocket-server/
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── main.py                   # FastAPI server (equivalent to server.ts)
├── session_manager.py        # Session handling (equivalent to sessionManager.ts)
├── function_handlers.py      # Function definitions (equivalent to functionHandlers.ts)
├── types.py                  # Type definitions (equivalent to types.ts)
├── twiml.xml                 # TwiML template
└── utils.py                  # Utility functions
```

## 🚀 Setup

1. **Install Dependencies**:
   ```bash
   cd python-websocket-server
   pip install -r requirements.txt
   ```

2. **Environment Setup**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Run Server**:
   ```bash
   python main.py
   # Or with uvicorn directly:
   uvicorn main:app --host 0.0.0.0 --port 8081 --reload
   ```

## 🔧 Key Changes Explained

### 1. Server Setup (server.ts → main.py)
- **Express.js** → **FastAPI**: Modern async Python web framework
- **http.createServer()** → **uvicorn**: ASGI server for FastAPI
- **CORS middleware** → **FastAPI CORS middleware**

### 2. WebSocket Handling
- **ws.WebSocketServer** → **FastAPI WebSocket**
- Connection routing via URL path parameters
- Async/await pattern maintained

### 3. Session Management
- **JavaScript objects** → **Python dataclasses/Pydantic models**
- **WebSocket references** → **FastAPI WebSocket objects**
- **Event handling** → **Async functions with try/catch**

### 4. Function Calling
- **TypeScript interfaces** → **Pydantic models**
- **JSON.parse()** → **json.loads()**
- **Promise-based handlers** → **Async functions**

## 🌟 Improvements Over Original

1. **Type Safety**: Pydantic models for request/response validation
2. **Better Error Handling**: Python exception handling with detailed logging
3. **Auto Documentation**: FastAPI generates OpenAPI docs automatically
4. **Testing**: Easier unit testing with pytest
5. **Deployment**: Standard Python deployment options (Docker, etc.)

## 📡 API Endpoints

- `GET /` - Health check
- `GET /public-url` - Returns the public URL
- `POST /twiml` - Returns TwiML for Twilio webhook
- `GET /tools` - Returns available function schemas
- `WebSocket /call` - Twilio call connection
- `WebSocket /logs` - Frontend logging connection

## 🔗 Integration Points

This Python server maintains full compatibility with:
- Twilio Voice API
- OpenAI Realtime API  
- Original frontend webapp
- ngrok tunneling

## 🐍 Python-Specific Features

1. **Type Hints**: Full type annotations for better IDE support
2. **Async/Await**: Native async support for better performance
3. **Context Managers**: Proper resource cleanup
4. **Logging**: Python logging module integration
5. **Configuration**: Environment-based configuration management

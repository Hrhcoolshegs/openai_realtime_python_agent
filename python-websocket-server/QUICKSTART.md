# Quick Setup Guide for Python WebSocket Server

## 🚀 Quick Start

1. **Navigate to the Python server directory:**
   ```bash
   cd python-websocket-server
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key and ngrok URL
   ```

4. **Start the server:**
   ```bash
   python start.py
   # OR
   python main.py
   # OR
   uvicorn main:app --host 0.0.0.0 --port 8081 --reload
   ```

## 🔧 Environment Setup

Create a `.env` file with:
```
OPENAI_API_KEY="your_openai_api_key_here"
PUBLIC_URL="https://your-ngrok-url.ngrok-free.app"
PORT=8081
HOST=0.0.0.0
LOG_LEVEL=INFO
```

## 🌐 Running with ngrok

In a separate terminal:
```bash
ngrok http 8081
```

Copy the forwarding URL to your `.env` file as `PUBLIC_URL`.

## 🧪 Testing

- Health check: `http://localhost:8081/`
- TwiML endpoint: `http://localhost:8081/twiml`
- Available tools: `http://localhost:8081/tools`
- WebSocket endpoints:
  - `/call` - For Twilio connections
  - `/logs` - For frontend connections

## 📦 Production Deployment

Using Gunicorn:
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8081
```

Using Docker:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## 🔍 Troubleshooting

1. **Import errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`
2. **WebSocket connection issues**: Check that ngrok is running and PUBLIC_URL is correct
3. **OpenAI API errors**: Verify your API key is valid and has Realtime API access
4. **Port conflicts**: Change PORT in .env if 8081 is already in use

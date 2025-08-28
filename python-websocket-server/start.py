#!/usr/bin/env python3
"""
Startup script for the Python WebSocket Server.

This script provides an easy way to start the server with proper
environment setup and dependency checking.
"""

import sys
import subprocess
import os
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3.8, 0):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python version: {sys.version.split()[0]}")


def check_requirements():
    """Check if required packages are installed."""
    try:
        import fastapi
        import uvicorn
        import websockets
        import httpx
        import dotenv
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing package: {e.name}")
        return False


def install_requirements():
    """Install requirements from requirements.txt."""
    requirements_file = Path(__file__).parent / "requirements.txt"
    if not requirements_file.exists():
        print("Error: requirements.txt not found")
        return False
    
    print("Installing requirements...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✓ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install requirements")
        return False


def check_environment():
    """Check environment variables."""
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_key = os.getenv("OPENAI_API_KEY")
    public_url = os.getenv("PUBLIC_URL")
    
    if not openai_key or openai_key == "your_openai_api_key_here":
        print("✗ OPENAI_API_KEY not set or using placeholder value")
        print("  Please update your .env file with a valid OpenAI API key")
        return False
    
    if not public_url or public_url == "https://your-ngrok-url.ngrok-free.app":
        print("⚠ PUBLIC_URL not set or using placeholder value")
        print("  This is required for Twilio webhook integration")
        print("  Run 'ngrok http 8081' and update PUBLIC_URL in .env")
    
    print("✓ Environment variables configured")
    return True


def start_server():
    """Start the FastAPI server."""
    print("\n🚀 Starting Python WebSocket Server...")
    print("   Server will be available at: http://localhost:8081")
    print("   TwiML endpoint: http://localhost:8081/twiml")
    print("   Tools endpoint: http://localhost:8081/tools")
    print("   WebSocket /call endpoint for Twilio")
    print("   WebSocket /logs endpoint for frontend")
    print("\n   Press Ctrl+C to stop the server\n")
    
    try:
        # Import and run the server
        from main import main
        main()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)


def main():
    """Main startup function."""
    print("🐍 Python WebSocket Server Startup")
    print("=" * 40)
    
    # Check Python version
    check_python_version()
    
    # Check and install requirements if needed
    if not check_requirements():
        print("\nInstalling missing requirements...")
        if not install_requirements():
            sys.exit(1)
        
        # Check again after installation
        if not check_requirements():
            print("Failed to install all requirements")
            sys.exit(1)
    
    # Check environment
    if not check_environment():
        print("\nPlease fix environment configuration and try again")
        sys.exit(1)
    
    # Start the server
    start_server()


if __name__ == "__main__":
    main()

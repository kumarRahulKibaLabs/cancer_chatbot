from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from chatbot.websocket import websocket_chat
import uvicorn
import logging
import os
from contextlib import asynccontextmanager
from collections import defaultdict
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Initialize FastAPI app
app = FastAPI()

# CORS middleware - replace with your frontend domain in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # For local testing; update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory rate limiting storage (IP -> (count, reset_time))
rate_limit_store = defaultdict(lambda: {"count": 0, "reset_time": datetime.now() + timedelta(hours=1)})
RATE_LIMIT = 100  # Max 100 connections per hour per IP

# Manual rate limiting for WebSocket
async def check_rate_limit(websocket: WebSocket) -> bool:
    client_ip = websocket.client.host
    now = datetime.now()
    
    # Reset count if the hour has passed
    if now >= rate_limit_store[client_ip]["reset_time"]:
        rate_limit_store[client_ip] = {"count": 0, "reset_time": now + timedelta(hours=1)}
    
    # Check and increment
    if rate_limit_store[client_ip]["count"] >= RATE_LIMIT:
        return False
    rate_limit_store[client_ip]["count"] += 1
    return True

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Medical Insurance Chatbot",
        "websocket_info": "Connect to the WebSocket endpoint at /chat"
    }

# WebSocket endpoint with manual rate limiting
@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    if not await check_rate_limit(websocket):
        await websocket.close(code=1013, reason="Rate limit exceeded (100/hour)")
        logging.info(f"Rate limit exceeded for IP: {websocket.client.host}")
        return
    
    logging.info("WebSocket connection established")
    try:
        await websocket_chat(websocket)
    except WebSocketDisconnect:
        logging.info("WebSocket disconnected")
    except Exception as e:
        logging.error(f"Error in WebSocket: {e}")
        await websocket.close(code=1011)  # Internal error

# Global exception handler
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled exception at {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(status_code=500, content={"message": "Internal server error"})

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting up application...")
    yield
    logging.info("Shutting down application...")

app.lifespan = lifespan

# Run the app
if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
    )


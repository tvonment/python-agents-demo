"""
Main application module for the multi-agent system.
"""
import os
import logging
import time
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from semantic_kernel.contents import ChatHistory
from dotenv import load_dotenv

from agents import OrchestratorAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

# Create logger for this module
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
logger.info("🔧 Environment variables loaded")


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    thread_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    thread_id: str


# Global variables for agents
orchestrator: Optional[OrchestratorAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    global orchestrator
    
    logger.info("🚀 Starting Multi-Agent System...")
    startup_time = time.time()
    
    # Startup: Initialize agents
    endpoint = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    logger.info(f"📍 Configured endpoint: {endpoint}")
    logger.info(f"🤖 Configured deployment: {deployment}")
    
    if not endpoint:
        logger.error("❌ Missing AZURE_AI_FOUNDRY_ENDPOINT")
        raise ValueError("Missing required environment variable: AZURE_AI_FOUNDRY_ENDPOINT")
    
    if not deployment:
        logger.error("❌ Missing AZURE_OPENAI_DEPLOYMENT_NAME")
        raise ValueError("Missing required environment variable: AZURE_OPENAI_DEPLOYMENT_NAME")
    
    try:
        orchestrator = OrchestratorAgent()
        startup_completed = time.time() - startup_time
        logger.info(f"✅ Multi-Agent System initialized successfully in {startup_completed:.2f}s")
        logger.info(f"🌐 API will be available on the configured host and port")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize system: {e}")
        raise
    
    yield
    
    # Shutdown: Cleanup if needed
    logger.info("🛑 Shutting down Multi-Agent System...")
    orchestrator = None
    logger.info("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Multi-Agent System",
    description="A Semantic Kernel-based multi-agent system with Orchestrator and QnA agents",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    client_ip = request.client.host
    method = request.method
    url = str(request.url)
    
    logger.info(f"🌐 HTTP {method} {url} from {client_ip}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    status_code = response.status_code
    
    logger.info(f"📤 HTTP {method} {url} -> {status_code} in {process_time:.2f}s")
    
    return response

# Store chat histories (in production, use proper storage)
chat_histories = {}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Multi-Agent System API", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.info("🏥 Health check requested")
    status = {
        "status": "healthy", 
        "agents": {
            "orchestrator": orchestrator is not None
        }
    }
    logger.info(f"📊 Health status: {status}")
    return status


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the multi-agent system."""
    request_start = time.time()
    request_id = f"req_{int(time.time() * 1000)}"
    
    logger.info(f"🎯 [{request_id}] NEW CHAT REQUEST")
    logger.info(f"📨 [{request_id}] Message: '{request.message[:100]}{'...' if len(request.message) > 100 else ''}'")
    logger.info(f"🧵 [{request_id}] Thread ID: {request.thread_id or 'NEW'}")
    
    if not orchestrator:
        logger.error(f"❌ [{request_id}] Orchestrator agent not initialized")
        raise HTTPException(status_code=500, detail="Orchestrator agent not initialized")
    
    try:
        # Get or create chat history
        if request.thread_id and request.thread_id in chat_histories:
            chat_history = chat_histories[request.thread_id]
            history_count = len([msg for msg in chat_history.messages])
            logger.info(f"📚 [{request_id}] Retrieved existing thread with {history_count} messages")
        else:
            chat_history = ChatHistory()
            logger.info(f"📝 [{request_id}] Created new chat history thread")
        
        # Get response from orchestrator
        logger.info(f"🤖 [{request_id}] Sending request to Orchestrator...")
        orchestrator_start = time.time()
        
        response = await orchestrator.handle_request(request.message, chat_history)
        
        orchestrator_time = time.time() - orchestrator_start
        logger.info(f"✅ [{request_id}] Orchestrator completed in {orchestrator_time:.2f}s")
        
        # Store the chat history for future use
        thread_id = request.thread_id or f"thread_{len(chat_histories)}"
        chat_histories[thread_id] = chat_history
        
        total_time = time.time() - request_start
        logger.info(f"🎉 [{request_id}] CHAT REQUEST COMPLETED in {total_time:.2f}s")
        logger.info(f"📤 [{request_id}] Response: '{response[:100]}{'...' if len(response) > 100 else ''}'")
        logger.info(f"💾 [{request_id}] Stored thread: {thread_id}")
        
        return ChatResponse(response=response, thread_id=thread_id)
        
    except Exception as e:
        error_time = time.time() - request_start
        logger.error(f"❌ [{request_id}] CHAT REQUEST FAILED after {error_time:.2f}s: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "localhost")
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"🌐 Starting server on {host}:{port}")
    logger.info("📝 Logging level: INFO")
    logger.info("🔄 Reload enabled for development")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

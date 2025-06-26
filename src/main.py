"""
Main application module for the multi-agent system.
"""
import os
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

from agents import OrchestratorAgent

# Load environment variables
load_dotenv()


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
    
    # Startup: Initialize agents
    endpoint = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    if not endpoint or not deployment_name:
        raise ValueError(
            "Missing required environment variables: "
            "AZURE_AI_FOUNDRY_ENDPOINT and AZURE_OPENAI_DEPLOYMENT_NAME"
        )
    
    orchestrator = OrchestratorAgent(endpoint, deployment_name)
    print(f"✅ Initialized Orchestrator Agent with endpoint: {endpoint}")
    
    yield
    
    # Shutdown: Cleanup if needed
    orchestrator = None


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

# Store chat threads (in production, use proper storage)
chat_threads = {}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Multi-Agent System API", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "agents": {"orchestrator": orchestrator is not None}}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the multi-agent system."""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator agent not initialized")
    
    try:
        # Get or create thread
        thread = chat_threads.get(request.thread_id) if request.thread_id else None
        
        # Get response from orchestrator
        response_parts = []
        async for response in orchestrator.handle_request(request.message, thread):
            if response.content:
                response_parts.append(response.content)
            
            # Store the thread for future use
            if response.thread:
                thread_id = request.thread_id or f"thread_{len(chat_threads)}"
                chat_threads[thread_id] = response.thread
        
        full_response = " ".join(response_parts)
        thread_id = request.thread_id or f"thread_{len(chat_threads) - 1}"
        
        return ChatResponse(response=full_response, thread_id=thread_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "localhost")
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

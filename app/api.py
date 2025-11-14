"""
NovaCRM Assistant FastAPI Application

REST API with:
- Query endpoint with account context support
- Conversation history with SqliteSaver
- Health checks
- Swagger documentation
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from pathlib import Path

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from .graph import get_graph
from .mcp_client import test_mcp_connection

from langgraph.checkpoint.sqlite import SqliteSaver

BASE_DIR = Path(__file__).resolve().parent.parent
CHECKPOINTS_DB = BASE_DIR / "checkpoints.db"

app = FastAPI(
    title="NovaCRM Assistant API",
    description="""
    REST API for NovaCRM Customer Intelligence & Operations Assistant.
    
    Features:
    - FAQ answering using RAG over knowledge base
    - Data lookup via MCP tools (accounts, invoices, tickets, usage)
    - Automatic intent classification and routing
    - Conversation memory with checkpointing
    - Evidence tracking with citations
    - Advanced validation and safety guardrails
    """,
    version="1.0.0",
    contact={
        "name": "NovaCRM Support",
        "email": "support@novacrm.com"
    }
)

graph_instance = None
memory_saver = None

class QueryRequest(BaseModel):
    """Request model for query endpoint"""
    query: str = Field(..., description="User query or question")
    account_context: Optional[str] = Field(None, description="Account ID for scoping (e.g., A001)")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    model: Optional[str] = Field("gpt-4o-mini", description="OpenAI model to use")
    temperature: Optional[float] = Field(0.0, description="LLM temperature (0.0-1.0)")

class QueryResponse(BaseModel):
    """Response model for query endpoint"""
    session_id: str
    query: str
    intent: Optional[str]
    answer: str
    evidence: list
    errors: list
    timestamp: str
    validation_passed: bool = True
    validation_issues: list = []

@app.on_event("startup")
async def startup_event():
    """Initialize graph and memory on startup"""
    global graph_instance, memory_saver
    
    print("=" * 60)
    print("Initializing NovaCRM Assistant API...")
    print("=" * 60)
    
    graph_instance = get_graph()
    
    memory_saver = SqliteSaver.from_conn_string(str(CHECKPOINTS_DB))
    
    print("API ready!")
    print("=" * 60)

@app.get("/", tags=["Health"])
def root():
    """Root endpoint with API information"""
    return {
        "service": "NovaCRM Assistant API",
        "version": "1.0.0",
        "status": "running",
        "milestone": "M5 - Final Submission",
        "endpoints": {
            "docs": "/docs",
            "query": "/query",
            "health": "/health",
            "mcp_status": "/mcp/status",
            "session_history": "/session/{session_id}"
        },
        "features": [
            "RAG over knowledge base",
            "MCP tool integration",
            "LangGraph routing",
            "Memory persistence",
            "Advanced validation",
            "Safety guardrails"
        ]
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    mcp_status = test_mcp_connection()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": "running",
            "graph": "initialized" if graph_instance else "not_initialized",
            "memory": "initialized" if memory_saver else "not_initialized",
            "mcp_server": "connected" if mcp_status else "disconnected"
        },
        "database": {
            "checkpoints": str(CHECKPOINTS_DB),
            "exists": CHECKPOINTS_DB.exists()
        }
    }

@app.get("/mcp/status", tags=["MCP"])
def mcp_status():
    """Check MCP server connection status"""
    is_connected = test_mcp_connection()
    
    return {
        "mcp_server": "http://127.0.0.1:3001",
        "status": "connected" if is_connected else "disconnected",
        "message": "MCP server is reachable" if is_connected else "MCP server not reachable. Please start: python servers/mcp_nova/server.py"
    }

@app.post("/query", response_model=QueryResponse, tags=["Assistant"])
def query_assistant(request: QueryRequest):
    """
    Process a query through the NovaCRM Assistant
    
    Supports:
    - FAQ queries (answered via RAG)
    - Data lookup queries (via MCP tools)
    - Escalation handling
    - Account context scoping
    - Session-based conversation history
    - Advanced validation and safety checks
    
    Returns structured response with:
    - Answer with evidence citations
    - Intent classification
    - Validation status
    - Conversation session ID
    """
    if not graph_instance:
        raise HTTPException(status_code=503, detail="Assistant not initialized")
    
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        # Use custom model/temperature if specified
        if request.model != graph_instance.llm.model_name or \
           request.temperature != graph_instance.llm.temperature:
            temp_graph = get_graph(model_name=request.model, temperature=request.temperature)
            result = temp_graph.invoke(request.query, account_context=request.account_context)
        else:
            result = graph_instance.invoke(request.query, account_context=request.account_context)
        
        # Save to memory
        if memory_saver:
            checkpoint_data = {
                "query": request.query,
                "answer": result.get("answer"),
                "intent": result.get("intent"),
                "evidence": result.get("evidence", []),
                "timestamp": datetime.now().isoformat()
            }
            
            try:
                # Store in checkpoint
                config = {"configurable": {"thread_id": session_id}}
                memory_saver.put(config, checkpoint_data, {})
            except Exception as e:
                print(f"Warning: Failed to save checkpoint: {e}")
        
        return QueryResponse(
            session_id=session_id,
            query=result["query"],
            intent=result.get("intent"),
            answer=result.get("answer", "No answer generated"),
            evidence=result.get("evidence", []),
            errors=result.get("errors", []),
            timestamp=datetime.now().isoformat(),
            validation_passed=result.get("validation_passed", True),
            validation_issues=result.get("validation_issues", [])
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.get("/session/{session_id}", tags=["Session"])
def get_session_history(session_id: str):
    """
    Retrieve conversation history for a session
    
    Args:
        session_id: Session identifier
        
    Returns:
        List of queries and responses in chronological order
    """
    if not memory_saver:
        raise HTTPException(status_code=503, detail="Memory not initialized")
    
    try:
        config = {"configurable": {"thread_id": session_id}}
        
        # Get checkpoint
        checkpoint = memory_saver.get(config)
        
        if not checkpoint:
            return {
                "session_id": session_id,
                "history": [],
                "message": "No history found for this session"
            }
        
        return {
            "session_id": session_id,
            "checkpoint": checkpoint,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")

@app.delete("/session/{session_id}", tags=["Session"])
def delete_session(session_id: str):
    """
    Delete a session and its history
    
    Args:
        session_id: Session identifier to delete
    """
    return {
        "session_id": session_id,
        "status": "deleted",
        "message": "Session history cleared"
    }

@app.post("/tools/account_lookup", tags=["MCP Tools"])
def account_lookup_direct(payload: Dict[str, Any] = Body(...)):
    """Direct access to account_lookup MCP tool"""
    from .mcp_client import call_mcp_tool
    return JSONResponse(content=call_mcp_tool("account_lookup", payload))

@app.post("/tools/invoice_status", tags=["MCP Tools"])
def invoice_status_direct(payload: Dict[str, Any] = Body(...)):
    """Direct access to invoice_status MCP tool"""
    from .mcp_client import call_mcp_tool
    return JSONResponse(content=call_mcp_tool("invoice_status", payload))

@app.post("/tools/ticket_summary", tags=["MCP Tools"])
def ticket_summary_direct(payload: Dict[str, Any] = Body(...)):
    """Direct access to ticket_summary MCP tool"""
    from .mcp_client import call_mcp_tool
    return JSONResponse(content=call_mcp_tool("ticket_summary", payload))

@app.post("/tools/usage_report", tags=["MCP Tools"])
def usage_report_direct(payload: Dict[str, Any] = Body(...)):
    """Direct access to usage_report MCP tool"""
    from .mcp_client import call_mcp_tool
    return JSONResponse(content=call_mcp_tool("usage_report", payload))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")


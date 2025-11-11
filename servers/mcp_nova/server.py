"""
NovaCRM MCP Server
Purpose:
    A production-ready MCP server exposing 5 tools for NovaCRM operations:
    - account_lookup: Get account details by ID or company name
    - invoice_status: Retrieve invoice details and payment status
    - ticket_summary: Get open tickets and SLA risks
    - usage_report: Get API/email/storage usage vs plan limits
    - kb_search: Search knowledge base documents
    
Architecture:
    - Uses FastMCP for protocol implementation
    - Runs both MCP (port 3000) and REST API (port 3001)
    - All tools return JSON with 'explanation' and 'source' fields
    - Robust error handling with descriptive messages
"""

from fastmcp import FastMCP
from typing import Dict, Any
import threading
from pathlib import Path

from tools import account_lookup, invoice_status, ticket_summary, usage_report, kb_search

BASE_DIR = Path(__file__).resolve().parent.parent.parent

mcp = FastMCP(name="NovaCRM_MCP_Server")

@mcp.tool(
    name="account_lookup",
    description="Look up account details by account_id or company name. Returns plan, tier, CSM, renewal date, and billing cycle."
)
def tool_account_lookup(account_id: str = None, company: str = None) -> Dict[str, Any]:
    """
    Retrieve account information from accounts.csv
    Args:
        account_id: Account ID (e.g., A001)
        company: Company name (case-insensitive)
    Returns:
        JSON with account details or error
    """
    return account_lookup(account_id=account_id, company=company)

@mcp.tool(
    name="invoice_status",
    description="Get invoice details for an account. Can filter by period (YYYY-MM) or specific invoice_id. Returns payment status, amounts, and summary."
)
def tool_invoice_status(account_id: str, period: str = None, invoice_id: str = None) -> Dict[str, Any]:
    """
    Retrieve invoice information from invoices.csv
    Args:
        account_id: Account ID (required)
        period: Month filter in YYYY-MM format (optional)
        invoice_id: Specific invoice ID (optional)
    Returns:
        JSON with invoice details and summary
    """
    return invoice_status(account_id=account_id, period=period, invoice_id=invoice_id)

@mcp.tool(
    name="ticket_summary",
    description="Get summary of support tickets for an account. Returns open tickets, SLA risks, and status breakdown for the specified time window."
)
def tool_ticket_summary(account_id: str, window_days: int = 90) -> Dict[str, Any]:
    """
    Retrieve ticket summary from tickets.csv
    Args:
        account_id: Account ID (required)
        window_days: Number of days to look back (default 90)
    Returns:
        JSON with ticket counts, open tickets, and SLA risks
    """
    return ticket_summary(account_id=account_id, window_days=window_days)

@mcp.tool(
    name="usage_report",
    description="Get API calls, email sends, and storage usage for a specific month. Compares usage against plan limits and warns if over 80%."
)
def tool_usage_report(account_id: str, month: str) -> Dict[str, Any]:
    """
    Retrieve usage metrics from usage.csv
    Args:
        account_id: Account ID (required)
        month: Month in YYYY-MM format (required)
    Returns:
        JSON with usage metrics, limits, percentages, and warnings
    """
    return usage_report(account_id=account_id, month=month)

@mcp.tool(
    name="kb_search",
    description="Search NovaCRM knowledge base documents for product information, FAQs, and documentation. Returns relevant document chunks."
)
def tool_kb_search(query: str, k: int = 5) -> Dict[str, Any]:
    """
    Search knowledge base using keyword matching
    Args:
        query: Search query string
        k: Maximum number of results (default 5)
    Returns:
        JSON with matching documents and content
    """
    return kb_search(query=query, k=k)

def start_rest_api():
    """
    Start REST API facade on port 3001 for HTTP access to MCP tools
    """
    from fastapi import FastAPI, Body
    from fastapi.responses import JSONResponse
    import uvicorn
    
    app = FastAPI(
        title="NovaCRM MCP REST API",
        description="REST facade for NovaCRM MCP tools. Provides HTTP access to account, invoice, ticket, usage, and knowledge base tools.",
        version="1.0.0"
    )
    
    @app.get("/")
    def root():
        return {
            "service": "NovaCRM MCP REST API",
            "version": "1.0.0",
            "tools": [
                "account_lookup",
                "invoice_status",
                "ticket_summary",
                "usage_report",
                "kb_search"
            ],
            "docs": "/docs"
        }
    
    @app.post("/tools/account_lookup", tags=["Account"])
    def http_account_lookup(payload: Dict[str, Any] = Body(...)):
        """Look up account details by account_id or company name"""
        return JSONResponse(content=account_lookup(**payload))
    
    @app.post("/tools/invoice_status", tags=["Invoice"])
    def http_invoice_status(payload: Dict[str, Any] = Body(...)):
        """Get invoice details and payment status"""
        return JSONResponse(content=invoice_status(**payload))
    
    @app.post("/tools/ticket_summary", tags=["Support"])
    def http_ticket_summary(payload: Dict[str, Any] = Body(...)):
        """Get open tickets and SLA risks"""
        return JSONResponse(content=ticket_summary(**payload))
    
    @app.post("/tools/usage_report", tags=["Usage"])
    def http_usage_report(payload: Dict[str, Any] = Body(...)):
        """Get usage metrics vs plan limits"""
        return JSONResponse(content=usage_report(**payload))
    
    @app.post("/tools/kb_search", tags=["Knowledge Base"])
    def http_kb_search(payload: Dict[str, Any] = Body(...)):
        """Search knowledge base documents"""
        return JSONResponse(content=kb_search(**payload))
    
    uvicorn.run(app, host="127.0.0.1", port=3001, log_level="info")

if __name__ == "__main__":
    print("=" * 60)
    print("NovaCRM MCP Server Starting...")
    print("=" * 60)
    print(f"MCP Protocol:  http://127.0.0.1:3000")
    print(f"REST API:      http://127.0.0.1:3001")
    print(f"Swagger Docs:  http://127.0.0.1:3001/docs")
    print(f"Data Path:     {BASE_DIR / 'data'}")
    print("=" * 60)
    
    rest_thread = threading.Thread(target=start_rest_api, daemon=True)
    rest_thread.start()
    
    mcp.run(
        transport="stdio"
    )


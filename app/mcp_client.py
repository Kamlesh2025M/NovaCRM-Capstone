"""
MCP Client for NovaCRM Assistant

Provides synchronous access to MCP tools running on the server
"""

import requests
from typing import Dict, Any, List

MCP_REST_BASE_URL = "http://127.0.0.1:3001/tools"

AVAILABLE_TOOLS = [
    "account_lookup",
    "invoice_status",
    "ticket_summary",
    "usage_report",
    "kb_search"
]

def call_mcp_tool(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call an MCP tool via REST API
    
    Args:
        tool_name: Name of the tool to call
        params: Dictionary of parameters
        
    Returns:
        Tool result as dictionary
    """
    if tool_name not in AVAILABLE_TOOLS:
        return {
            "error": f"Unknown tool: {tool_name}",
            "explanation": f"Available tools: {', '.join(AVAILABLE_TOOLS)}"
        }
    
    url = f"{MCP_REST_BASE_URL}/{tool_name}"
    
    try:
        response = requests.post(url, json=params, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"HTTP {response.status_code}",
                "explanation": response.text[:200]
            }
    
    except requests.exceptions.ConnectionError:
        return {
            "error": "MCP server not reachable",
            "explanation": f"Could not connect to {MCP_REST_BASE_URL}. Ensure MCP server is running."
        }
    
    except requests.exceptions.Timeout:
        return {
            "error": "Request timeout",
            "explanation": f"Tool {tool_name} took too long to respond"
        }
    
    except Exception as e:
        return {
            "error": f"{type(e).__name__}",
            "explanation": str(e)
        }

def get_mcp_tools() -> List[str]:
    """
    Get list of available MCP tools
    
    Returns:
        List of tool names
    """
    return AVAILABLE_TOOLS.copy()

def test_mcp_connection() -> bool:
    """
    Test if MCP server is reachable
    
    Returns:
        True if server is running, False otherwise
    """
    try:
        response = requests.get("http://127.0.0.1:3001/", timeout=5)
        return response.status_code == 200
    except:
        return False


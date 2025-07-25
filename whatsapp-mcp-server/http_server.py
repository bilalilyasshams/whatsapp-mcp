import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os

# Import MCP tools
from main import mcp

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="WhatsApp MCP HTTP API",
    description="HTTP wrapper for WhatsApp MCP server to enable n8n integration",
    version="1.0.0"
)

# Enable CORS for n8n integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class MCPRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = {}

class MCPResponse(BaseModel):
    success: bool
    data: Any = None
    error: str = None

class HealthResponse(BaseModel):
    status: str
    version: str
    available_tools: List[str]

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring"""
    tools = list(mcp._tools.keys())
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        available_tools=tools
    )

# List available tools
@app.get("/tools")
async def list_tools():
    """Get list of available WhatsApp MCP tools"""
    tools = {}
    for name, tool in mcp._tools.items():
        tools[name] = {
            "name": name,
            "description": tool.func.__doc__ or "No description available",
            "parameters": tool.func.__annotations__
        }
    return {"tools": tools}

# Execute MCP tool
@app.post("/execute", response_model=MCPResponse)
async def execute_tool(request: MCPRequest):
    """Execute a WhatsApp MCP tool"""
    try:
        logger.info(f"Executing tool: {request.tool_name} with args: {request.arguments}")
        
        if request.tool_name not in mcp._tools:
            raise HTTPException(
                status_code=400, 
                detail=f"Tool '{request.tool_name}' not found"
            )
        
        tool = mcp._tools[request.tool_name]
        result = await tool.func(**request.arguments)
        
        return MCPResponse(success=True, data=result)
        
    except Exception as e:
        logger.error(f"Error executing tool {request.tool_name}: {str(e)}")
        return MCPResponse(success=False, error=str(e))

# Convenience endpoints for common WhatsApp operations

@app.post("/whatsapp/send-message")
async def send_whatsapp_message(
    chat_jid: str,
    message: str,
    quoted_message_id: Optional[str] = None
):
    """Send a WhatsApp message"""
    try:
        from main import send_message
        result = await send_message(chat_jid, message, quoted_message_id)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/whatsapp/send-file")
async def send_whatsapp_file(
    chat_jid: str,
    file_path: str,
    caption: Optional[str] = None
):
    """Send a file via WhatsApp"""
    try:
        from main import send_file
        result = await send_file(chat_jid, file_path, caption)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error sending file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/whatsapp/chats")
async def get_whatsapp_chats(
    query: Optional[str] = None,
    limit: int = 20,
    page: int = 0,
    include_last_message: bool = True,
    sort_by: str = "last_active"
):
    """Get WhatsApp chats"""
    try:
        from main import list_chats
        result = await list_chats(query, limit, page, include_last_message, sort_by)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error getting chats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/whatsapp/messages")
async def get_whatsapp_messages(
    after: Optional[str] = None,
    before: Optional[str] = None,
    sender_phone_number: Optional[str] = None,
    chat_jid: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 20,
    page: int = 0,
    include_context: bool = True,
    context_before: int = 1,
    context_after: int = 1
):
    """Get WhatsApp messages"""
    try:
        from main import list_messages
        result = await list_messages(
            after, before, sender_phone_number, chat_jid, query,
            limit, page, include_context, context_before, context_after
        )
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error getting messages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/whatsapp/contacts")
async def search_whatsapp_contacts(query: str):
    """Search WhatsApp contacts"""
    try:
        from main import search_contacts
        result = await search_contacts(query)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error searching contacts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("MCP_PORT", 8000))
    host = os.getenv("MCP_HOST", "0.0.0.0")
    
    logger.info(f"Starting WhatsApp MCP HTTP API on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

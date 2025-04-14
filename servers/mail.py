import random
from typing import Any

import httpx
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

# Create server
app = FastAPI(title="Message Server")
mcp = FastMCP("Echo Server")


@mcp.tool()
def get_email(name: str) -> str:
    """Gets the email address of the individual named"""
    values = {"ato": "atotoffah@gmail.com", "nana": "n.brown@4th-ir.com"}

    name = name.lower()

    for k, v in values.items():
        if k.find(name):
            return name

    return "No email found"


@mcp.tool()
def compose_email(email_address: str, message: str) -> str:
    """Composes an email address for the address specified using the message"""

    mail = f"""
    To: {email_address}
    
    This is a test email
    The message is '{message}'
    
    Best regards,
    Auto
    """

    return mail


app.mount(path="/", app=mcp.sse_app())

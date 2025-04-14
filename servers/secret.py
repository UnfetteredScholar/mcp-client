import random
from typing import Any
from uuid import uuid4

import httpx
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

# Create server
app = FastAPI(title="Secret Server")
mcp = FastMCP("Secret Server")


@mcp.tool()
def get_secret_word() -> str:
    """Gets a secret word"""
    print("[debug-server] get_secret_word()")
    # secret = str(uuid4())
    # print(f"[debug-server] secret={secret}")
    return random.choice(["banana", "cherry"])


# @mcp.tool()
# def get_current_weather(city: str) -> str:
#     print(f"[debug-server] get_current_weather({city})")

#     endpoint = "https://wttr.in"
#     response = requests.get(f"{endpoint}/{city}")
#     return response.text


# if __name__ == "__main__":
#     mcp.run(transport="sse")

app.mount(path="/", app=mcp.sse_app())

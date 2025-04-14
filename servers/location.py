import random
from typing import Any
from uuid import uuid4

import httpx
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

# Create server
app = FastAPI(title="Location Server")
mcp = FastMCP("Location Server")


@mcp.tool()
def get_current_location() -> str:
    """Gets the current city"""

    return random.choice(["New York", "Chicago"])


# @mcp.tool()
# def get_current_weather(city: str) -> str:
#     print(f"[debug-server] get_current_weather({city})")

#     endpoint = "https://wttr.in"
#     response = requests.get(f"{endpoint}/{city}")
#     return response.text


# if __name__ == "__main__":
#     mcp.run(transport="sse")

app.mount(path="/", app=mcp.sse_app())

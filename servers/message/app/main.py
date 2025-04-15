import random
from typing import Any

import httpx
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

# Create server
app = FastAPI(title="Message Server")
mcp = FastMCP("Echo Server")


@mcp.tool()
def get_message(secret_word: str) -> str:
    """Gets the message corresponding to the secret word"""
    print("[debug-server] get_message()")
    if secret_word == "banana":
        return f"I love {secret_word} milkshakes"
    elif secret_word == "cherry":
        return f"I hate {secret_word} pie"
    else:
        return "Invalid secret word"


app.mount(path="/", app=mcp.sse_app())

# @mcp.tool()
# def get_current_weather(city: str) -> str:
#     print(f"[debug-server] get_current_weather({city})")

#     endpoint = "https://wttr.in"
#     response = requests.get(f"{endpoint}/{city}")
#     return response.text


# if __name__ == "__main__":
#     mcp.run(transport="sse")

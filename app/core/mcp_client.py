from contextlib import AsyncExitStack, asynccontextmanager
from typing import AsyncGenerator

from agents import Agent, Runner
from agents.mcp import MCPServerSse
from agents.model_settings import ModelSettings


class MCPClient:
    def __init__(self, mcp_server_addresses: list[str]):
        self._mcp_server_addresses = mcp_server_addresses
        self.exit_stack = AsyncExitStack()

    @property
    def mcp_server_addresses(self) -> list[str]:
        return self._mcp_server_addresses

    @mcp_server_addresses.setter
    def mcp_server_addresses(self, value: list[str]):
        self._mcp_server_addresses = value

    async def run(self, messages: list[dict]) -> str:
        """Runs the prompt using the MCP Client Agent"""
        mcp_servers = []
        for address in self._mcp_server_addresses:
            mcp_servers.append(
                await self.exit_stack.enter_async_context(
                    MCPServerSse(
                        name="SSE Python Server",
                        params={
                            "url": address,
                        },
                    )
                )
            )

        agent = Agent(
            name="Assistant",
            instructions="Use the tools to answer the questions.",
            mcp_servers=mcp_servers,
            model_settings=ModelSettings(tool_choice="required"),
        )

        result = await Runner.run(starting_agent=agent, input=messages)

        return result.final_output

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def get_mcp_client() -> AsyncGenerator[MCPClient, None]:
    """Gets an MCP Client"""
    mcp_client = MCPClient([])
    try:
        yield mcp_client
    finally:
        await mcp_client.cleanup()


async def main():
    client = MCPClient(
        [
            # "http://localhost:8000/sse",
            "http://localhost:8001/sse",
            "http://localhost:8002/sse",
        ]
    )
    try:

        res = await client.run(
            [
                {
                    "role": "user",
                    "content": "Get the weather for my current city/ location",
                }
            ]
        )

        print(res)
    except Exception as ex:
        print(f"Error: {ex}")
    finally:
        # print("cleanup")
        await client.cleanup()

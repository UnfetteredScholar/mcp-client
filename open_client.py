import asyncio
from contextlib import AsyncExitStack
from typing import Any

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServerSse
from agents.model_settings import ModelSettings
from dotenv import load_dotenv

load_dotenv()


class MCPClient:
    def __init__(self, mcp_server_addresses: list[str]):
        self.mcp_server_addresses = mcp_server_addresses
        self.exit_stack = AsyncExitStack()

    async def run(self, messages: list[dict]) -> str:
        mcp_servers = []
        for address in self.mcp_server_addresses:
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


async def main():
    client = MCPClient(["http://localhost:8000/sse"])
    try:
        trace_id = gen_trace_id()
        with trace(workflow_name="SSE Example", trace_id=trace_id):
            print(
                f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n"
            )

            res = await client.run(
                [
                    {
                        "role": "user",
                        "content": "What's the weather in New York?",
                    }
                ]
            )

            print(res)
    except Exception as ex:
        print(f"Error: {ex}")
    finally:
        print("cleanup")
        await client.cleanup()


if __name__ == "__main__":

    asyncio.run(main())

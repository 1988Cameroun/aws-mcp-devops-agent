import asyncio
import os
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

async def run_agent(query: str):
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "aws_mcp_agent.server"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Get available tools from MCP server
            tools_result = await session.list_tools()
            tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                for tool in tools_result.tools
            ]

            print(f"\n Agent tools available: {[t['name'] for t in tools]}\n")
            print(f"Query: {query}\n")
            print("-" * 50)

            messages = [{"role": "user", "content": query}]

            # Agentic loop
            while True:
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4096,
                    tools=tools,
                    messages=messages
                )

                if response.stop_reason == "end_turn":
                    for block in response.content:
                        if hasattr(block, "text"):
                            print(f"\nAgent Response:\n{block.text}")
                    break

                # Handle tool calls
                tool_uses = [b for b in response.content 
                            if b.type == "tool_use"]
                
                if not tool_uses:
                    break

                messages.append({
                    "role": "assistant",
                    "content": response.content
                })

                tool_results = []
                for tool_use in tool_uses:
                    print(f"Calling tool: {tool_use.name}")
                    result = await session.call_tool(
                        tool_use.name, 
                        tool_use.input
                    )
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": result.content[0].text
                    })

                messages.append({
                    "role": "user",
                    "content": tool_results
                })

if __name__ == "__main__":
    query = "Give me a full infrastructure report: list all EC2 instances, S3 buckets, IAM roles, and VPC network configuration."
    asyncio.run(run_agent(query))
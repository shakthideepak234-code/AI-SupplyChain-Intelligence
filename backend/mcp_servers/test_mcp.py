import asyncio

from fastmcp import Client
from backend.mcp_servers.supply_chain_mcp import mcp


async def main():

    async with Client(mcp) as client:

        tools = await client.list_tools()

        print("\nAvailable MCP Tools:")

        for tool in tools:
            print("-", tool.name)

        result = await client.call_tool("total_demand", {})

        print("\nTotal Demand Result:")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
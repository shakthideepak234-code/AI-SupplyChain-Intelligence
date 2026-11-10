import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0,
    timeout=60,
)

SYSTEM_PROMPT = """
You are a Supply Chain Intelligence Assistant.

Answer questions using the available MCP tools.

Rules:
1. Use tools to retrieve demand data.
2. Never invent numerical values.
3. Clearly explain results.
4. If data is unavailable, say so.
5. Current weekly demand data covers only CA_1 store.
"""
async def create_supply_chain_agent():

    client = MultiServerMCPClient({
        "supply_chain": {
            "command": sys.executable,
            "args": [
                "-m",
                "backend.mcp_servers.supply_chain_mcp"
            ],
            "transport": "stdio",
            "cwd": str(PROJECT_ROOT)
        }
    })

    tools = await client.get_tools()

    print("Connected MCP Tools:")
    for tool in tools:
        print("-", tool.name)

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT
    )

    return agent

async def main():

    client = MultiServerMCPClient({
        "supply_chain": {
            "command": sys.executable,
            "args": [
                "-m",
                "backend.mcp_servers.supply_chain_mcp"
            ],
            "transport": "stdio",
            "cwd": str(PROJECT_ROOT)
        }
    })

    tools = await client.get_tools()

    print("Connected MCP Tools:")
    for tool in tools:
        print("-", tool.name)

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT
    )

    response = await agent.ainvoke({
        "messages": [
            {
                "role": "user",
                "content": "What is the total recorded demand?"
            }
        ]
    })

    print("\nAgent Response:")
    print(response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
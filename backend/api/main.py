
import asyncio

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.agents.supply_chain_agent import create_supply_chain_agent


app = FastAPI(
    title="AI Supply Chain Intelligence API",
    description="API for supply chain demand intelligence",
    version="1.0.0"
)


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "AI Supply Chain Intelligence API is running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}



@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        agent = await create_supply_chain_agent()

        response = await agent.ainvoke({
            "messages": [
                {"role": "user", "content": request.question}
            ]
        })

        content = response["messages"][-1].content

        if isinstance(content, list):
            answer = "".join(
                item["text"]
                for item in content
                if isinstance(item, dict) and item.get("type") == "text"
            )
        else:
            answer = content

        return {"answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import os

from dotenv import load_dotenv
from fastapi import FastAPI

from graph import graph

load_dotenv()

app = FastAPI()


@app.post("/chat")
async def chat(payload: dict):

    query = payload["query"]

    result = graph.invoke(
        {
            "query": query
        }
    )

    return {
        "answer": result["final_answer"],
        "plan": result["plan"],
        "verification": result["verification"]
    }
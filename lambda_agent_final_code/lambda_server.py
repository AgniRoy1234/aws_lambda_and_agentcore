import os
import json
from dotenv import load_dotenv
from strands import Agent, tool
from strands.models.litellm import LiteLLMModel

# Lambda does not need dotenv if env vars are set in AWS
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# -----------------------
# LLM Configuration
# -----------------------
llm = LiteLLMModel(
    client_args={"api_key": GROQ_API_KEY},
    model_id="groq/openai/gpt-oss-120b",
    reasoning=False
)

# -----------------------
# Anime Tool
# -----------------------
@tool
def anime_qa_tool(query: str) -> str:
    anime_agent = Agent(
        model=llm,
        system_prompt="""
        You are an expert Anime Q/A assistant.

        You ONLY answer questions related to anime, manga,
        characters, studios, arcs, and Japanese animation.
        Use at most 2 small sentences. Do not go into details.

        If unrelated, say:
        "This agent only handles anime-related questions."
        """,
        tools=[]
    )

    response = anime_agent(query)
    return str(response)


# -----------------------
# Router Agent
# -----------------------
anime_router_agent = Agent(
    model=llm,
    name="Anime QA Agent",
    description="Handles only anime-related questions.",
    system_prompt="""
    If the query is about anime, call anime_qa_tool.
    Otherwise respond:
    "This agent only handles anime-related queries."
    """,
    tools=[anime_qa_tool],
)

# -----------------------
# Lambda Handler
# -----------------------
def lambda_handler(event, context):

    try:
        print("Event")
        print(event)
        # Handle both direct Lambda URL and API Gateway
        if "body" in event and event["body"] is not None:
            if isinstance(event["body"], str):
                print("This is body")
                print(event['body'])
                body = json.loads(event["body"])
            else:
                body = event["body"]
        else:
            body = event  # direct invocation
            

        query = body.get("query")

        if not query:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Query is required"})
            }

        response = anime_router_agent(query)
        
        print("This is response")
        print(response)

        return {
            "statusCode": 200,
            "body": json.dumps({"response": str(response)})
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
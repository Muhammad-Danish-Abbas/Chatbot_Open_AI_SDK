import os
import chainlit as cl

from dotenv import load_dotenv, find_dotenv

# Assuming 'agents' is a custom module you have; make sure the classes below exist there
from agents import Agent, RunConfig, AsyncOpenAI, OpenAIChatCompletionsModel, Runner
from openai.types.responses import ResponseTextDeltaEvent
from agents.tool import function_tool
# Load environment variables
load_dotenv(find_dotenv())

# Get API key from .env file
gemini_api_key = "AIzaSyCzc0QZT4ruBmTNQLXrUlgAzpbORi6puDg"

# Step 1: Provider
provider = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",

)

# Step 2: Model
model = OpenAIChatCompletionsModel(
     model="gemini-2.0-flash",
     openai_client=provider,
)

# Step 3: Config
run_config = RunConfig(
    model=model,
    model_provider=provider,
    tracing_disabled=True
)

@function_tool("get_weather")
def get_weather(location: str, unit: str = "C") -> str:
  """
  Fetch the weather for a given location, returning a short description.
  """
  # Example logic
  return f"The weather in {location} is 22 degrees {unit}."

# Step 4: Agent
agent1 = Agent(
    instructions="You are a helpful assistant and Fetch the weather for a given location.",
    name="Panaverity support agent",
    tools=[get_weather]
)

@cl.on_chat_start
async def handle_chat_start():
    cl.user_session.set("history",[])
    await cl.Message(
        content="Hello, Wellcome to the DANISH's Chatbot:-").send()

@cl.on_message
async def main(message: cl.Message):
    history = cl.user_session.get("history")

    # Our custom logic goes here...
    # Send a fake response back to the user
    
    msg = cl.Message(content="")
    await msg.send()


    # Standed interface
    history.append({"role":"user","content":message.content})
    result = Runner.run_streamed(
     agent1,
     input=history,
    run_config=run_config,   
    )

    async for event in result.stream_events():
            if event.type == "raw_response_event" and hasattr(event.data, 'delta'):
                token = event.data.delta
                await msg.stream_token(token)
       


    history.append({"role":"assistant","content":result.final_output})
    cl.user_session.set("history",history)
    #await cl.Message(content=result.final_output,).send()

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

llm="qwen3:4b"
model = init_chat_model(
    model=llm,
    model_provider="ollama",
    temperature=0,
    timeout=300,
    max_tokens=25000,
    reasoning=True
)
agent = create_agent(
    model=model,
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

# Run the agent
agent.invoke(
    {"messages": [{"role": "user", "content": "What is the weather in San Francisco?"}]}
)
"""
Tool Calling: Instead of the user deciding when to call a function, the LLM reads the user's question and decides:
  1. "I need to call get_current_weather with location=Bengaluru"
  2. It outputs a structured JSON tool-call request
  3. Code is executed to call the function and send the result back
  4. The LLM uses that result to form a natural language answer.
"""

import json
from ollama import chat, ChatResponse

# This is the tool we want the LLM to use when it needs weather data. 
# In a real app, this would call a weather API.
def get_current_weather(location: str) -> str:
    """Returns fake weather data for a given location."""
    # Fake data — in real life, you'd call an API here
    weather_data = {
        "Bengaluru": "sunny, 28°C",
        "London": "cloudy, 14°C",
        "New York": "rainy, 18°C",
        "Tokyo": "clear, 22°C",
    }

    # Defensive: if the LLM passes a dict instead of a string, extract the value
    if isinstance(location, dict):
        location = location.get("value", location.get("location", str(location)))

    conditions = weather_data.get(location, "partly cloudy, 20°C")
    return f"The current weather in {location} is {conditions}."


# This is the JSON schema that defines the tool for the LLM. It tells the LLM:
#   a. What function to call (name)
#   b. What it does (description)
#   c. What parameters it takes and their types
# The LLM reads this and decides whether to call it based on the user's question.

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather for a given location/city",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name, e.g. 'Bengaluru', 'London'",
                    },
                },
                "required": ["location"],
            },
        },
    }
]

# This is a mapping from tool names (as defined in the JSON schema) to the actual Python functions we want to 
# execute when the LLM calls them.
available_functions = {
    "get_current_weather": get_current_weather,
}

# This function handles the entire flow of asking a question, letting the LLM decide if it needs to call a tool,
# executing that tool, and then sending the result back to the LLM for a final answer.
def ask(question: str):
    print(f"\n{'='*60}")
    print(f"USER: {question}")
    print(f"{'='*60}")

    messages = [
        {"role": "system", "content": (
            "You are a helpful assistant with access to tools. "
            "ONLY use the get_current_weather tool when the user explicitly asks about weather. "
            "For any other question, answer directly without calling any tool. "
            "IMPORTANT: When a tool returns a result, that result IS the real data. "
            "Report the tool result to the user as a factual answer. "
            "NEVER say 'I don't have real-time data' or 'I cannot access' — the tool already fetched the data for you."
        )},
        {"role": "user", "content": question},
    ]

    # First call: Send the question + tool definitions to the LLM
    print("\nSending question to LLM (with tool definitions)...")
    response: ChatResponse = chat(
        model="llama3.2",
        messages=messages,
        # This is where we tell the LLM about the tools it can use. The LLM will read this and decide if it needs 
        # to call any of these tools based on the user's question.
        tools=tools,
    )

    # Check if the LLM wants to call a tool
    if response.message.tool_calls:
        for tool_call in response.message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = tool_call.function.arguments

            print(f"\nLLM wants to call: {tool_name}({json.dumps(tool_args)})")

            # Execute the actual function
            function_to_call = available_functions.get(tool_name)
            if not function_to_call:
                result = f"Error: Unknown tool '{tool_name}'"
            else:
                try:
                    result = function_to_call(**tool_args)
                except Exception as e:
                    result = f"Error calling {tool_name}: {e}"

            print(f"Tool result: {result}")

            # Add the LLM's tool-call request to the conversation
            messages.append(response.message)

            messages.append({
                "role": "tool",
                "content": result,
            })

            messages.append({
                "role": "user",
                "content": f"The tool returned: {result}. Please use this information to answer my original question.",
            })

        # Second call: Send the tool result back to the LLM for a final answer
        print("\nSending tool result back to LLM for final answer...")
        final_response: ChatResponse = chat(
            model="llama3.2",
            messages=messages,
        )
        print(f"\nASSISTANT: {final_response.message.content}")

    else:
        # The LLM answered directly without needing any tools
        print(f"\nASSISTANT (no tool needed): {response.message.content}")


if __name__ == "__main__":
    # This SHOULD trigger the tool (it's asking about weather)
    ask("What's the weather like in Bengaluru?")
    # This SHOULD also trigger the tool
    ask("Tell me the current weather in London")
    # This should NOT trigger the tool (not a weather question)
    ask("What is the capital of France?")

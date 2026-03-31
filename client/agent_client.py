import asyncio
from pathlib import Path
from datetime import datetime
import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Path to the F1 server (relative to this file)
SERVER_PATH = Path(__file__).parent.parent.joinpath("server", "f1_server.py")

server_params = StdioServerParameters(
    command="uv",
    args=["run", "python", str(SERVER_PATH)],
    env=None,
)


def convert_mcp_tool_to_ollama(mcp_tool) -> dict:
    """
    Converts an MCP Tool object into the format Ollama expects.
    
    Ollama tool schema:
    {
        "type": "function",
        "function": {
            "name": "tool_name",
            "description": "...",
            "parameters": {
                "type": "object",
                "properties": { ... },
                "required": [ ... ]
            }
        }
    }
    """
    return {
        "type": "function",
        "function": {
            "name": mcp_tool.name,
            "description": mcp_tool.description,
            "parameters": mcp_tool.inputSchema,
        }
    }


async def run_agent():
    """
    Main agent loop:
    1. Connect to the MCP server and discover tools
    2. Enter a chat loop where the user can ask F1 questions
    3. When Ollama wants to call a tool, execute it via MCP
    4. Feed the result back to Ollama for a natural language answer
    """
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Discover all tools from the F1 server
            mcp_tools_result = await session.list_tools()
            mcp_tools = mcp_tools_result.tools
            
            print(f"Connected to F1 server. Discovered {len(mcp_tools)} tools:")
            for tool in mcp_tools:
                print(f"  - {tool.name}")
            print()

            # Convert MCP tools to Ollama format
            ollama_tools = [convert_mcp_tool_to_ollama(tool) for tool in mcp_tools]

            # Chat loop
            current_date = datetime.now().strftime("%B %d, %Y")
            messages = [
                {
                    "role": "system",
                    "content": (
                        f"You are an expert Formula 1 assistant with access to real-time F1 data. "
                        f"Today's date is {current_date}. When users say 'this season', 'current season', "
                        f"or 'latest', they mean the {datetime.now().year} F1 season. "
                        f"Use the available tools to fetch accurate data and provide detailed answers."
                    )
                }
            ]
            
            print("F1 Chat Agent ready. Ask me anything about Formula 1!")
            print("(Type 'exit' to quit)\n")

            while True:
                user_input = input("You: ").strip()
                if user_input.lower() in ["exit", "quit"]:
                    print("Goodbye!")
                    break

                if not user_input:
                    continue

                # Add user message to conversation history
                messages.append({"role": "user", "content": user_input})

                # Send to Ollama with tools
                response = ollama.chat(
                    model="llama3.2",
                    messages=messages,
                    tools=ollama_tools,
                )

                # Check if Ollama wants to call a tool
                if response.message.tool_calls:
                    # Ollama decided to use a tool instead of answering directly
                    print(f"[Agent is calling {len(response.message.tool_calls)} tool(s)...]")
                    
                    # Append the assistant's tool-call message to history
                    # (Ollama needs this in the conversation to track what it requested)
                    messages.append(response.message)

                    # Execute each tool call via MCP
                    for tool_call in response.message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = tool_call.function.arguments
                        
                        print(f"  → Calling {tool_name} with args: {tool_args}")

                        try:
                            mcp_result = await session.call_tool(tool_name, tool_args)
                            tool_result_text = mcp_result.content[0].text
                        except Exception as e:
                            # If the tool call fails, return the error to Ollama
                            tool_result_text = f"Error calling {tool_name}: {str(e)}"
                            print(f"Tool call failed: {e}")

                        messages.append({
                            "role": "tool",
                            "content": tool_result_text,
                        })

                    response = ollama.chat(
                        model="llama3.2",
                        messages=messages,
                        tools=ollama_tools,
                    )

                assistant_message = response.message.content
                print(f"Assistant: {assistant_message}\n")
                messages.append({"role": "assistant", "content": assistant_message})


if __name__ == "__main__":
    asyncio.run(run_agent())

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
from pathlib import Path

# Define the parameters to launch the local server script
SERVER_PATH = Path(__file__).parent.parent / "server" / "f1_server.py"
server_params = StdioServerParameters(
    command="uv",
    args=["run", "python", str(SERVER_PATH)],
    env=None,
)

async def run():
    # Establish the stdio connection
    async with stdio_client(server_params) as (read, write):
        # Initialize and manage the client session
        async with ClientSession(read, write) as session:
            await session.initialize()

            # list_tools() returns a ListToolsResult — the list is at .tools
            # each item is a Tool object with .name and .description attributes
            tools = await session.list_tools()
            print("Available tools from the server:")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            # call_tool() takes arguments as a dict, returns a CallToolResult
            # the text response is at .content[0].text
            standings = await session.call_tool("get_driver_standings", {"season": 2024})
            print("\n2024 Driver Standings:")
            print(standings.content[0].text)

            race_result = await session.call_tool("get_race_result", {"season": 2024, "round": 1})
            print("\n2024 Round 1 Race Result:")
            print(race_result.content[0].text)

            # read_resource() returns a ReadResourceResult — text is at .contents[0].text
            resources = await session.read_resource("f1://drivers/current")
            print("\nCurrent Drivers:")
            print(resources.contents[0].text)


if __name__ == "__main__":
    asyncio.run(run())
import asyncio
from fastmcp import Client, FastMCP

# In-memory server (ideal for testing)
# server = FastMCP("Cupcake MCP")
# client = Client(server)

# HTTP server
client = Client("http://127.0.0.1:8000/sse/")

async def main():
    try:
        async with client:
            # Basic server interaction
            await client.ping()

            # List available operations
            tools = await client.list_tools()
            resources = await client.list_resources()
            prompts = await client.list_prompts()
            
            # print("tools============="+tools)
            # Execute operations
            print("=============")
            results = await client.call_tool("search", {"query": "cupcakes"})
            # print(result)
            for result in results.structured_content["results"]:
                print(f"- {result['id']} {result['title']}")

            result = await client.call_tool("fetch", {"id": "47"})
            for i in result.structured_content:
                print(f"- {i}: {result.structured_content[i]}")

            print(f"result: {result.structured_content['title']}")

    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
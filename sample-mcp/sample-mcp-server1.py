# =============================================================================
# Sample - MCP Server
# Created: 2, Sep 2025
# Updated: 2, Sep 2025
# Writer: Ted, Jung
# Description: MCP Server example using FastMCP
# =============================================================================

import json
from pathlib import Path
from fastmcp.server import FastMCP
from pydantic import BaseModel
from regex import P



# Set the root directory to the parent of this script's directory
# to read the sample data file.
# It could be replace with a database or other data source.
ROOT_DIR = Path(__file__).parent.parent
RECORDS = json.loads(ROOT_DIR.joinpath("data", "records.json").read_text())
LOOKUP = {r["id"]: r for r in RECORDS}


# Build Pydatic models for the tool responses
# Single result and a single list to return multiple results
class SearchResult(BaseModel):
    id: str
    title: str
    text: str

class SearchResultPage(BaseModel):
    results: list[SearchResult]

class FetchResult(BaseModel):
    id: str
    title: str
    text: str
    url: str | None = None
    metadata: dict[str, str] | None = None



# Create the MCP server and define tools (search, fetch)
def create_server():
    mcp = FastMCP(name="Cupcake MCP", instructions="Search cupcake orders")

    @mcp.tool()
    async def search(query: str) -> SearchResultPage:
        """
        Search for cupcake orders – keyword match.

        Returns a SearchResultPage containing a list of SearchResult items.
        """
        toks = query.lower().split()
        results: list[SearchResult] = []
        for r in RECORDS:
            hay = " ".join(
                [
                    r.get("title", ""),
                    r.get("text", ""),
                    " ".join(r.get("metadata", {}).values()),
                ]
            ).lower()
            if any(t in hay for t in toks):
                results.append(
                    SearchResult(id=r["id"], title=r.get("title", ""), text=r.get("text", ""))
                )

        # Return the Pydantic model (FastMCP will serialise it for us)
        return SearchResultPage(results=results)

    @mcp.tool()
    async def fetch(id: str) -> FetchResult:
        """
        Fetch a cupcake order by ID.

        Returns a FetchResult model.
        """
        if id not in LOOKUP:
            raise ValueError("unknown id")

        r = LOOKUP[id]
        return FetchResult(
            id=r["id"],
            title=r.get("title", ""),
            text=r.get("text", ""),
            url=r.get("url"),
            metadata=r.get("metadata"),
        )

    return mcp


# run the server using SSE transport on localhost:8000
# You can also use other ASGI servers like Uvicorn or Hypercorn
if __name__ == "__main__":
    create_server().run(transport="sse", host="127.0.0.1", port=8000)
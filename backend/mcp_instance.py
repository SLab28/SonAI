"""Singleton FastMCP instance. Import this instead of mcp_server to avoid circular imports."""
from fastmcp import FastMCP

mcp = FastMCP(
    name="sonai",
    instructions=(
        "SonAI audio analysis and soundscape generation tools. "
        "Analyse audio files using analysis tools first (Source → Transform → Measure → Infer), "
        "then use generation tools (Compose → Render) to produce non-vocal flow-state music. "
        "Always call insight_composer before any generation tool. "
        "Never generate vocals or lyric-based content."
    ),
)


@mcp.tool
async def ping() -> dict:
    """Health check — confirms MCP server is running."""
    return {"status": "ok", "server": "sonai"}

import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


ROOT = Path(__file__).resolve().parents[1]


async def main() -> None:
    params = StdioServerParameters(
        command=os.environ.get("MCP_PYTHON", sys.executable),
        args=[str(ROOT / "server.py")],
        cwd=str(ROOT),
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = [tool.name for tool in tools.tools]
            expected = {
                "gazette_status",
                "gazette_categories",
                "search_gazette",
                "get_gazette",
                "browse_gazette",
            }
            assert set(names) == expected, names

            status_result = await session.call_tool("gazette_status", {})
            status = json.loads(status_result.content[0].text)
            assert status["ok"] is True, status
            assert status["status"] == 200, status

            search_result = await session.call_tool(
                "search_gazette", {"category": "gavaaidhu", "max_results": 1}
            )
            search = json.loads(search_result.content[0].text)
            assert search["status"] == 200, search
            assert search["results"], search
            assert search["results"][0]["source"].startswith("https://"), search

            detail_result = await session.call_tool("get_gazette", {"url_or_id": "7539"})
            detail = json.loads(detail_result.content[0].text)
            assert detail["status"] == 200, detail
            assert detail["title"], detail
            assert detail["pdf_url"].endswith(".pdf"), detail

            print(json.dumps({"tools": names, "status": status, "first_result": search["results"][0], "detail": detail}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())

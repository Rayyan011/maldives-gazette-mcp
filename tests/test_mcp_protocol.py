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
                "iulaan_categories",
                "translate_iulaan_query",
                "search_iulaan",
                "get_iulaan",
                "read_iulaan_attachment",
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

            tender_result = await session.call_tool(
                "search_iulaan", {"announcement_type": "beelan", "open_only": True, "max_results": 1}
            )
            tender = json.loads(tender_result.content[0].text)
            assert tender["status"] == 200, tender
            assert tender["results"], tender
            assert tender["results"][0]["source"].startswith("https://"), tender

            job_result = await session.call_tool(
                "search_iulaan", {"announcement_type": "vazeefaa", "open_only": True, "max_results": 1}
            )
            jobs = json.loads(job_result.content[0].text)
            assert jobs["status"] == 200, jobs
            assert jobs["results"], jobs

            iulaan_detail_result = await session.call_tool("get_iulaan", {"url_or_id": "405846"})
            iulaan_detail = json.loads(iulaan_detail_result.content[0].text)
            assert iulaan_detail["status"] == 200, iulaan_detail
            assert iulaan_detail["title"], iulaan_detail
            assert iulaan_detail["attachments"], iulaan_detail
            assert iulaan_detail["employer"], iulaan_detail

            attachment_result = await session.call_tool(
                "read_iulaan_attachment",
                {"url": iulaan_detail["attachments"][0]["url"], "max_chars": 2000},
            )
            attachment = json.loads(attachment_result.content[0].text)
            assert attachment["characters"] > 0, attachment
            assert attachment["source"].endswith(".pdf"), attachment

            translation_result = await session.call_tool(
                "translate_iulaan_query", {"query": "software developer"}
            )
            translation = json.loads(translation_result.content[0].text)
            assert translation["translated_variants"], translation
            assert any("ސޮފްޓްވެއަރ" in variant for variant in translation["translated_variants"]), translation

            translated_search_result = await session.call_tool(
                "search_iulaan", {"query": "software developer", "announcement_type": "vazeefaa", "open_only": True, "max_results": 5}
            )
            translated_search = json.loads(translated_search_result.content[0].text)
            assert translated_search["query_variants"], translated_search
            assert translated_search["results"], translated_search

            print(json.dumps({"tools": names, "status": status, "first_result": search["results"][0], "detail": detail, "tender": tender["results"][0], "job": jobs["results"][0], "iulaan_detail": iulaan_detail, "attachment": {"source": attachment["source"], "characters": attachment["characters"], "truncated": attachment["truncated"]}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())

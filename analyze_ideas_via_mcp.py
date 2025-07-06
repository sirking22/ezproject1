import asyncio
import argparse
from notion_mcp_server import NotionMCPServer


def parse_args():
    parser = argparse.ArgumentParser(description="Run Notion MCP analysis for a database (completeness).")
    parser.add_argument("--db", dest="database_id", required=False, default=None, help="Notion database ID (default: IDEAS_DB from .env)")
    parser.add_argument("--freshness", dest="freshness_days", type=int, default=14, help="Freshness window in days")
    parser.add_argument("--tool", dest="tool", default="analyze_notion_completeness", help="MCP tool to run (analyze_notion_completeness, clean_notion_ideas)")
    parser.add_argument("--yadisk_url", dest="yadisk_url", required=False, default=None, help="Yandex.Disk public URL for image (for add_yadisk_image_as_notion_cover)")
    parser.add_argument("--page_id", dest="page_id", required=False, default=None, help="Notion page_id (for add_yadisk_image_as_notion_cover)")
    parser.add_argument("--image_url", dest="image_url", required=False, default=None, help="Image URL for Notion cover (for set_notion_cover_from_url)")
    return parser.parse_args()


async def main():
    args = parse_args()
    server = NotionMCPServer()
    # Ждём запуска async-сервера (он сразу готов, handlers зарегистрированы)

    print(f"▶️  Запускаю анализ базы через MCP-инструмент {args.tool}...", flush=True)

    # Вызываем инструмент напрямую через call_tool handler
    tool_args = {"database_id": args.database_id or server.default_database_id}
    if args.tool == "analyze_notion_completeness":
        tool_args["freshness_days"] = args.freshness_days
    if args.tool == "add_yadisk_image_as_notion_cover":
        if args.yadisk_url:
            tool_args["yadisk_url"] = args.yadisk_url
        if args.page_id:
            tool_args["page_id"] = args.page_id
    if args.tool == "set_notion_cover_from_url":
        if args.image_url:
            tool_args["image_url"] = args.image_url
        if args.page_id:
            tool_args["page_id"] = args.page_id
    result_list = list(await server.call_tool(
        args.tool,
        tool_args,
    ))
    print("\n===== MCP RESULT =====\n")
    if result_list:
        print(str(result_list[0]))
    print("\n======================\n")


if __name__ == "__main__":
    asyncio.run(main()) 
import os
from dotenv import load_dotenv
import json

# Путь к .env и mcp.json
ENV_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
MCP_JSON_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '.cursor', 'mcp.json')

load_dotenv(ENV_PATH)

notion_token = os.getenv('NOTION_TOKEN')
db_id = os.getenv('NOTION_IDEAS_DB_ID')

if not notion_token or not db_id:
    raise RuntimeError('NOTION_TOKEN или NOTION_IDEAS_DB_ID не найдены в .env')

mcp_config = {
    "mcpServers": {
        "notion-mcp-server": {
            "type": "command",
            "command": "python",
            "args": [
                "Z:/Файлы/VS code/notion_mcp_server.py"
            ],
            "env": {
                "NOTION_TOKEN": notion_token,
                "NOTION_DATABASE_ID": db_id
            }
        }
    }
}

with open(MCP_JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(mcp_config, f, ensure_ascii=False, indent=4)

print(f"mcp.json обновлён: {MCP_JSON_PATH}") 
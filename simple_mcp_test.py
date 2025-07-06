#!/usr/bin/env python3
"""
Максимально простой MCP сервер для тестирования
"""

import asyncio
import json
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SimpleMCPServer:
    """Максимально простой MCP сервер"""
    
    def __init__(self):
        self.server = Server("simple-mcp-server")
        
        # Создаем простой инструмент
        self.tools = [
            Tool(
                name="test_tool",
                description="Простой тестовый инструмент",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"}
                    },
                    "required": ["message"]
                }
            )
        ]
        
        logger.info(f"CREATED {len(self.tools)} TOOLS")
        
        # Регистрируем обработчики
        self.server.list_tools()(self.list_tools)
        self.server.call_tool()(self.handle_call_tool)
        
    async def list_tools(self, *args, **kwargs):
        """Возвращает список инструментов"""
        logger.info(f"LIST_TOOLS CALLED, RETURNING {len(self.tools)} TOOLS")
        for tool in self.tools:
            logger.info(f"  - {tool.name}: {tool.description}")
        return self.tools

    async def handle_call_tool(self, name: str, arguments: dict) -> list[TextContent]:
        """Обрабатывает вызовы инструментов"""
        logger.info(f"HANDLE_CALL_TOOL: name={name}, arguments={arguments}")
        return [TextContent(type="text", text=f"Simple response for {name}: {arguments}")]

async def main():
    """Основная функция"""
    server = SimpleMCPServer()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="simple-mcp-server",
                server_version="1.0.0",
                capabilities=server.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main()) 
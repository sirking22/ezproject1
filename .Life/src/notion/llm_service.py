"""LLM integration service for Notion."""
from typing import Dict, List, Optional, Any, Sequence
import logging
from datetime import datetime

from ..base_service import BaseService
from .service import NotionService
from ..llm.service import DeepseekService, LocalLLMService, LLMService
from ...config import settings
from ...models.notion_models import NotionPage, TextBlock, NotionBlock

logger = logging.getLogger(__name__)

class NotionLLMService(BaseService):
    """Service for LLM integration with Notion."""
    
    def __init__(self):
        """Initialize service."""
        super().__init__()
        self.notion = NotionService()
        self.llm: LLMService = (
            LocalLLMService() if settings.USE_LOCAL_MODEL else DeepseekService()
        )
        
    async def initialize(self) -> None:
        """Initialize services."""
        await self.notion.initialize()
        await self.llm.initialize()
        
    async def cleanup(self) -> None:
        """Cleanup resources."""
        await self.notion.cleanup()
        await self.llm.cleanup()
        
    async def analyze_task(self, task_id: str) -> Dict[str, Any]:
        """Analyze a task using LLM."""
        # Get task content
        task = await self.notion.get_page_content(task_id)
        
        # Extract text content
        text_content = []
        for block in task:
            if isinstance(block, TextBlock):
                text_content.append(block.paragraph.get("rich_text", [{}])[0].get("text", {}).get("content", ""))
                
        # Analyze with LLM
        analysis = await self.llm.analyze_text("\n".join(text_content))
        
        # Add analysis to task
        await self.notion.append_blocks(task_id, [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "AI Analysis"}
                    }]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": f"Summary: {analysis['summary']}"}
                    }]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": f"Sentiment: {analysis['sentiment']}"}
                    }]
                }
            }
        ])
        
        return analysis
        
    async def generate_learning_path(self, topic: str) -> NotionPage:
        """Generate a learning path for a topic."""
        # Generate learning path with LLM
        prompt = f"""Create a detailed learning path for {topic}.
Include the following sections:
1. Prerequisites
2. Core concepts
3. Practical exercises
4. Advanced topics
5. Resources

Format the response in clear sections with bullet points."""
        
        content = await self.llm.generate_text(prompt)
        
        # Create learning path structure
        properties = {
            "Name": {"title": [{"text": {"content": f"Learning Path: {topic}"}}]},
            "Status": {"select": {"name": "Not Started"}},
            "Type": {"select": {"name": "Learning Path"}},
            "Created": {"date": {"start": datetime.now().isoformat()}}
        }
        
        # Format content for Notion
        blocks = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": f"Learning Path for {topic}"}
                    }]
                }
            }
        ]
        
        # Add generated content
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": content}
                }]
            }
        })
        
        # Create page in Notion
        return await self.notion.create_page(
            self.notion.databases["learning"],
            properties,
            blocks
        )
        
    async def enhance_notes(self, page_id: str) -> Sequence[NotionBlock]:
        """Enhance notes with LLM-generated content."""
        # Get existing notes
        blocks = await self.notion.get_page_content(page_id)
        
        # Extract text content
        text_content = []
        for block in blocks:
            if isinstance(block, TextBlock):
                text_content.append(block.paragraph.get("rich_text", [{}])[0].get("text", {}).get("content", ""))
                
        # Generate enhancements
        text = "\n".join(text_content)
        
        suggestions = await self.llm.generate_suggestions(text)
        summary = await self.llm.generate_summary(text)
        topics = await self.llm.extract_topics(text)
        
        # Create enhancement blocks
        enhanced_blocks = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "AI-Enhanced Notes"}
                    }]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": f"Summary: {summary}"}
                    }]
                }
            },
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "Key Topics"}
                    }]
                }
            }
        ]
        
        # Add topics
        for topic in topics:
            enhanced_blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": topic}
                    }]
                }
            })
            
        # Add suggestions
        enhanced_blocks.extend([
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "Suggestions"}
                    }]
                }
            }
        ])
        
        for suggestion in suggestions:
            enhanced_blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": suggestion}
                    }]
                }
            })
            
        # Append enhanced content
        return await self.notion.append_blocks(page_id, enhanced_blocks)
        
    async def summarize_database(self, database_id: str) -> Dict[str, Any]:
        """Generate a summary of database content."""
        # Query database
        pages = await self.notion.query_database(database_id)
        
        # Extract content for analysis
        content = []
        for page in pages:
            blocks = await self.notion.get_page_content(page.id)
            for block in blocks:
                if isinstance(block, TextBlock):
                    content.append(block.paragraph.get("rich_text", [{}])[0].get("text", {}).get("content", ""))
                    
        # Analyze with LLM
        text = "\n".join(content)
        analysis = await self.llm.analyze_text(text)
        
        # Create summary page
        properties = {
            "Name": {"title": [{"text": {"content": "Database Summary"}}]},
            "Type": {"select": {"name": "Summary"}},
            "Created": {"date": {"start": datetime.now().isoformat()}}
        }
        
        blocks = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "Database Summary"}
                    }]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": analysis["summary"]}
                    }]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "Key Points"}
                    }]
                }
            }
        ]
        
        for point in analysis["key_points"]:
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": point}
                    }]
                }
            })
            
        await self.notion.create_page(database_id, properties, blocks)
        
        return analysis 
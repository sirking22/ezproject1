import logging
from typing import Optional, List, Dict, Any, Sequence
from notion_client import AsyncClient
from datetime import datetime, UTC
from .base import Repository
from ..models.base import TaskDTO, LearningProgressDTO
from ..utils.notion_formatter import (
    create_title_property,
    create_rich_text_property,
    create_select_property,
    create_multi_select_property,
    create_date_property,
    create_number_property,
    extract_title,
    extract_rich_text,
    extract_select,
    extract_multi_select,
    extract_date,
    extract_number
)
from ..utils.date_utils import parse_notion_date
from src.core.config import Settings

logger = logging.getLogger(__name__)

class NotionTaskRepository(Repository[TaskDTO]):
    """Repository implementation for Notion tasks."""
    
    def __init__(self, client: AsyncClient, database_id: str):
        self.client = client
        self.database_id = database_id
        logger.info(f"Initialized NotionTaskRepository with database_id: {database_id}")

    async def validate_database(self) -> tuple[bool, str]:
        """Validate database connection and structure"""
        try:
            # Try to retrieve database
            logger.info(f"Validating database {self.database_id}")
            database = await self.client.databases.retrieve(database_id=self.database_id)
            
            # Check required properties
            required_properties = {
                "Title": "title",
                "Status": "select",
                "Priority": "select",
                "Tags": "multi_select",
                "Description": "rich_text",
                "Due Date": "date"
            }
            
            missing_properties = []
            wrong_type_properties = []
            
            for prop_name, prop_type in required_properties.items():
                if prop_name not in database["properties"]:
                    missing_properties.append(prop_name)
                elif database["properties"][prop_name]["type"] != prop_type:
                    wrong_type_properties.append(f"{prop_name} (expected {prop_type}, got {database['properties'][prop_name]['type']})")
            
            if missing_properties or wrong_type_properties:
                error_msg = "Database validation failed:\n"
                if missing_properties:
                    error_msg += f"Missing properties: {', '.join(missing_properties)}\n"
                if wrong_type_properties:
                    error_msg += f"Wrong property types: {', '.join(wrong_type_properties)}"
                logger.error(error_msg)
                return False, error_msg
            
            logger.info("Database validation successful")
            return True, "Database structure is valid"
            
        except Exception as e:
            error_msg = f"Failed to validate database: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    async def get_tasks(self, limit: Optional[int] = None) -> List[TaskDTO]:
        """Get tasks from Notion database with optional limit"""
        tasks = await self.list()
        if limit:
            return tasks[:limit]
        return tasks

    async def get(self, id: str) -> Optional[TaskDTO]:
        """Get task by ID."""
        try:
            logger.debug(f"Fetching task with id: {id}")
            page = await self.client.pages.retrieve(page_id=id)
            task = self._to_dto(page)
            logger.debug(f"Successfully fetched task: {task.title}")
            return task
        except Exception as e:
            logger.error(f"Error fetching task {id}: {str(e)}")
            return None

    async def create(self, task: TaskDTO) -> TaskDTO:
        """Create new task."""
        try:
            logger.debug(f"Creating new task: {task.title}")
            properties = self._from_dto(task)
            response = await self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            created_task = self._to_dto(response)
            logger.info(f"Successfully created task: {created_task.title}")
            return created_task
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            raise

    async def update(self, id: str, task: TaskDTO) -> Optional[TaskDTO]:
        """Update existing task."""
        try:
            logger.debug(f"Updating task {id}: {task.title}")
            properties = self._from_dto(task)
            response = await self.client.pages.update(
                page_id=id,
                properties=properties
            )
            updated_task = self._to_dto(response)
            logger.info(f"Successfully updated task {id}: {updated_task.title}")
            return updated_task
        except Exception as e:
            logger.error(f"Error updating task {id}: {str(e)}")
            return None

    async def delete(self, id: str) -> bool:
        """Delete task by ID (archive in Notion)."""
        try:
            logger.debug(f"Archiving task: {id}")
            await self.client.pages.update(
                page_id=id,
                archived=True
            )
            logger.info(f"Successfully archived task: {id}")
            return True
        except Exception as e:
            logger.error(f"Error archiving task {id}: {str(e)}")
            return False

    async def list(self, params: Optional[Dict] = None) -> List[TaskDTO]:
        """List tasks with optional filtering."""
        try:
            # First validate database
            is_valid, error_msg = await self.validate_database()
            if not is_valid:
                logger.error(f"Database validation failed: {error_msg}")
                return []
                
            logger.info(f"Starting task listing with params: {params}")
            logger.info(f"Using database ID: {self.database_id}")
            
            query = {
                "database_id": self.database_id,
                "page_size": 100,  # Default page size
                "sorts": [],
                "filter": {}
            }
            
            if params:
                logger.info("Processing query parameters...")
                # Handle limit
                if "limit" in params:
                    query["page_size"] = params["limit"]
                    logger.info(f"Set page size to: {params['limit']}")
                
                # Handle filters
                filters = []
                
                # Status filter
                if "status" in params:
                    status_filter = params["status"]
                    logger.info(f"Processing status filter: {status_filter}")
                    if isinstance(status_filter, dict):
                        if "equals" in status_filter:
                            filters.append({
                                "property": "Status",
                                "select": {
                                    "equals": status_filter["equals"]
                                }
                            })
                            logger.info(f"Added equals status filter: {status_filter['equals']}")
                        elif "not_equals" in status_filter:
                            filters.append({
                                "property": "Status",
                                "select": {
                                    "does_not_equal": status_filter["not_equals"]
                                }
                            })
                            logger.info(f"Added not_equals status filter: {status_filter['not_equals']}")
                
                # Tags filter
                if "tags" in params:
                    tags_filter = params["tags"]
                    logger.info(f"Processing tags filter: {tags_filter}")
                    if isinstance(tags_filter, list):
                        for tag in tags_filter:
                            filters.append({
                                "property": "Tags",
                                "multi_select": {
                                    "contains": tag
                                }
                            })
                            logger.info(f"Added tag filter: {tag}")
                
                # Priority filter
                if "priority" in params:
                    priority_filter = params["priority"]
                    logger.info(f"Processing priority filter: {priority_filter}")
                    if isinstance(priority_filter, str):
                        filters.append({
                            "property": "Priority",
                            "select": {
                                "equals": priority_filter
                            }
                        })
                        logger.info(f"Added priority filter: {priority_filter}")
                
                # Combine filters with AND
                if filters:
                    if len(filters) == 1:
                        query["filter"] = filters[0]
                    else:
                        query["filter"] = {
                            "and": filters
                        }
                    logger.info(f"Final filter: {query['filter']}")
            
            logger.info(f"Executing Notion query: {query}")
            response = await self.client.databases.query(**query)
            logger.info(f"Got response from Notion with {len(response['results'])} results")
            
            tasks = []
            for page in response["results"]:
                try:
                    task = self._to_dto(page)
                    tasks.append(task)
                    logger.debug(f"Processed task: {task.title}")
                except Exception as e:
                    logger.error(f"Error processing task from page: {str(e)}")
                    continue
            
            logger.info(f"Successfully processed {len(tasks)} tasks")
            return tasks
        except Exception as e:
            logger.error(f"Error listing tasks: {str(e)}", exc_info=True)
            return []

    async def exists(self, id: str) -> bool:
        try:
            await self.client.pages.retrieve(page_id=id)
            return True
        except:
            return False

    def _to_dto(self, page: Dict[str, Any]) -> TaskDTO:
        """Convert Notion page to DTO."""
        props = page["properties"]
        return TaskDTO(
            id=page["id"],
            title=props["Title"]["title"][0]["text"]["content"],
            status=props["Status"]["select"]["name"],
            description=props.get("Description", {}).get("rich_text", [{}])[0].get("text", {}).get("content"),
            due_date=datetime.fromisoformat(props["Due Date"]["date"]["start"]) if props.get("Due Date") else None,
            created_at=datetime.fromisoformat(page["created_time"]),
            updated_at=datetime.fromisoformat(page["last_edited_time"])
        )
        
    def _from_dto(self, task: TaskDTO) -> Dict[str, Any]:
        """Convert DTO to Notion properties."""
            properties = {
            "Title": {"title": [{"text": {"content": task.title}}]},
            "Status": {"select": {"name": task.status}},
            }
            
            if task.description:
            properties["Description"] = {
                "rich_text": [{"text": {"content": task.description}}]
            }
            
            if task.due_date:
            properties["Due Date"] = {
                "date": {"start": task.due_date.isoformat()}
            }
            
        return properties

class NotionLearningRepository(Repository[LearningProgressDTO]):
    """Repository implementation for Notion learning progress."""
    
    def __init__(self, client: AsyncClient, database_id: str):
        self.client = client
        self.database_id = database_id

    async def get_items(self, limit: Optional[int] = None) -> List[LearningProgressDTO]:
        """Get learning progress items from Notion database with optional limit"""
        items = await self.list()
        if limit:
            return items[:limit]
        return items

    async def get(self, id: str) -> Optional[LearningProgressDTO]:
        """Get learning progress by ID."""
        try:
            page = await self.client.pages.retrieve(page_id=id)
            return self._to_dto(page)
        except Exception as e:
            # Log error and return None
            return None

    async def create(self, progress: LearningProgressDTO) -> LearningProgressDTO:
        """Create new learning progress."""
        try:
            page = await self.client.pages.create(
            parent={"database_id": self.database_id},
                properties=self._from_dto(progress)
        )
            return self._to_dto(page)
        except Exception as e:
            # Log error and re-raise
            raise

    async def update(self, id: str, progress: LearningProgressDTO) -> Optional[LearningProgressDTO]:
        """Update existing learning progress."""
        try:
            page = await self.client.pages.update(
                page_id=id,
                properties=self._from_dto(progress)
            )
            return self._to_dto(page)
        except Exception as e:
            # Log error and return None
            return None

    async def delete(self, id: str) -> bool:
        """Delete learning progress by ID (archive in Notion)."""
        try:
            await self.client.pages.update(
                page_id=id,
                archived=True
            )
            return True
        except Exception as e:
            # Log error and return False
            return False

    async def list(self, params: Optional[Dict] = None) -> List[LearningProgressDTO]:
        """List learning progress with optional filtering."""
        try:
            query = {"database_id": self.database_id}
            if params:
                query.update(params)
            pages = await self.client.databases.query(**query)
            return [self._to_dto(page) for page in pages["results"]]
        except Exception as e:
            # Log error and return empty list
            return []

    async def exists(self, id: str) -> bool:
        try:
            await self.client.pages.retrieve(page_id=id)
            return True
        except:
            return False

    def _to_dto(self, page: Dict[str, Any]) -> LearningProgressDTO:
        """Convert Notion page to DTO."""
        props = page["properties"]
        return LearningProgressDTO(
            task_id=props["Task"]["relation"][0]["id"],
            topic=props["Topic"]["select"]["name"],
            status=props["Status"]["select"]["name"],
            completion_rate=props["Completion Rate"]["number"],
            last_review=datetime.fromisoformat(props["Last Review"]["date"]["start"]),
            next_review=datetime.fromisoformat(props["Next Review"]["date"]["start"]) if props.get("Next Review") else None,
            notes=props.get("Notes", {}).get("rich_text", [{}])[0].get("text", {}).get("content"),
            created_at=datetime.fromisoformat(page["created_time"]),
            updated_at=datetime.fromisoformat(page["last_edited_time"])
        )
        
    def _from_dto(self, progress: LearningProgressDTO) -> Dict[str, Any]:
        """Convert DTO to Notion properties."""
        properties = {
            "Task": {"relation": [{"id": progress.task_id}]},
            "Topic": {"select": {"name": progress.topic}},
            "Status": {"select": {"name": progress.status}},
            "Completion Rate": {"number": progress.completion_rate},
            "Last Review": {"date": {"start": progress.last_review.isoformat()}},
        }
        
        if progress.next_review:
            properties["Next Review"] = {
                "date": {"start": progress.next_review.isoformat()}
            }
            
        if progress.notes:
            properties["Notes"] = {
                "rich_text": [{"text": {"content": progress.notes}}]
            }
            
        return properties 

class NotionRepository:
    """Repository for managing Notion database operations."""
    
    def __init__(self, settings: Settings):
        """Initialize Notion repository.
        
        Args:
            settings: Application settings containing Notion credentials
        """
        self.client = AsyncClient(auth=settings.NOTION_TOKEN)
        self.databases = settings.NOTION_DATABASES
        
    async def create_idea(self, idea_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new idea in Notion database.
        
        Args:
            idea_data: Idea data to store
            
        Returns:
            Created Notion page data
        """
        try:
            # Convert idea data to Notion properties
            properties = self._to_notion_properties(idea_data)
            
            # Create page in ideas database
            response = await self.client.pages.create(
                parent={"database_id": self.databases["ideas"]},
                properties=properties
            )
            
            # Convert response back to our format
            return self._from_notion_page(response)
            
        except Exception as e:
            logger.error(f"Error creating idea in Notion: {e}", exc_info=True)
            raise
            
    async def get_idea(self, idea_id: str) -> Optional[Dict[str, Any]]:
        """Get idea by ID from Notion.
        
        Args:
            idea_id: Notion page ID
            
        Returns:
            Idea data if found, None otherwise
        """
        try:
            # Get page from Notion
            response = await self.client.pages.retrieve(page_id=idea_id)
            
            # Convert to our format
            return self._from_notion_page(response)
            
        except Exception as e:
            logger.error(f"Error getting idea from Notion: {e}", exc_info=True)
            return None
            
    async def get_ideas(
        self,
        sort_by: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get ideas with optional sorting."""
        try:
            # Prepare query
            query = {
                "database_id": self.databases["ideas"],
                "page_size": limit
            }
            
            # Add sorting if specified
            if sort_by:
                query["sorts"] = [{
                    "property": sort_by,
                    "direction": "descending"
                }]
                
            # Query database
            response = await self.client.databases.query(**query)
            
            # Convert results
            return [
                self._from_notion_page(page)
                for page in response.get("results", [])
            ]
            
        except Exception as e:
            logger.error(f"Error getting ideas from Notion: {e}", exc_info=True)
            return []
            
    async def update_idea(self, idea_id: str, idea_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing idea in Notion.
        
        Args:
            idea_id: Notion page ID
            idea_data: Updated idea data
            
        Returns:
            Updated idea data if successful, None otherwise
        """
        try:
            # Convert to Notion properties
            properties = self._convert_to_notion_properties(idea_data)
            
            # Update page
            response = await self.client.pages.update(
                page_id=idea_id,
                properties=properties
            )
            
            return self._convert_from_notion(response)
            
        except Exception as e:
            logger.error(f"Error updating idea in Notion: {e}", exc_info=True)
            return None
            
    def _to_notion_properties(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert our data format to Notion properties."""
        properties = {
            "Title": {"title": [{"text": {"content": data["title"]}}]},
            "Description": {"rich_text": [{"text": {"content": data["description"]}}]},
            "Creator": {"rich_text": [{"text": {"content": data["creator"]}}]},
            "Status": {"select": {"name": data.get("status", "active")}},
            "Priority Score": {"number": float(data.get("priority_score", 1.0))},
            "Innovation Category": {"select": {"name": data.get("innovation_category", "product")}},
            "Market Size": {"rich_text": [{"text": {"content": data.get("market_size", "")}}]},
            "Market Analysis": {"rich_text": [{"text": {"content": data.get("market_analysis", "")}}]},
            "AI Insights": {"rich_text": [{"text": {"content": data.get("ai_insights", "")}}]},
            "Competitive Advantage": {"rich_text": [{"text": {"content": data.get("competitive_advantage", "")}}]},
            
            # Impact metrics
            "Potential Users": {"number": int(data["impact_metrics"]["potential_users"])},
            "Regions Affected": {"multi_select": [
                {"name": region} for region in data["impact_metrics"]["regions_affected"]
            ]},
            "SDG Goals": {"multi_select": [
                {"name": goal} for goal in data["impact_metrics"]["sdg_goals"]
            ]},
            "Environmental Impact": {"select": {"name": data["impact_metrics"]["environmental_impact"]}},
            "Social Impact": {"select": {"name": data["impact_metrics"]["social_impact"]}},
            "Economic Impact": {"select": {"name": data["impact_metrics"]["economic_impact"]}},
            
            # Implementation
            "Current Stage": {"select": {"name": data["implementation"]["current_stage"]}},
            "Tech Stack": {"multi_select": [
                {"name": tech} for tech in data["implementation"]["tech_stack"]
            ]},
            "Resource Requirements": {"multi_select": [
                {"name": req} for req in data["implementation"]["resource_requirements"]
            ]},
            "Development Stages": {"multi_select": [
                {"name": stage} for stage in data["implementation"]["development_stages"]
            ]},
            "Challenges": {"multi_select": [
                {"name": challenge} for challenge in data["implementation"]["challenges"]
            ]},
            "Solutions": {"multi_select": [
                {"name": solution} for solution in data["implementation"]["solutions"]
            ]},
            
            # Lists
            "Improvement Suggestions": {"multi_select": [
                {"name": sugg} for sugg in data.get("improvement_suggestions", [])
            ]},
            "Next Steps": {"multi_select": [
                {"name": step} for step in data.get("next_steps", [])
            ]},
            
            # Timestamps
            "Created At": {"date": {"start": data.get("created_at", datetime.utcnow()).isoformat()}},
        }
        
        if data.get("updated_at"):
            properties["Updated At"] = {
                "date": {"start": data["updated_at"].isoformat()}
            }

        return properties

    def _from_notion_page(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Notion page to our data format."""
        props = page["properties"]
        
        def get_title(prop: Dict[str, Any]) -> str:
            return prop.get("title", [{}])[0].get("text", {}).get("content", "")
            
        def get_rich_text(prop: Dict[str, Any]) -> str:
            return prop.get("rich_text", [{}])[0].get("text", {}).get("content", "")
            
        def get_select(prop: Dict[str, Any]) -> str:
            return prop.get("select", {}).get("name", "")
            
        def get_multi_select(prop: Dict[str, Any]) -> List[str]:
            return [item["name"] for item in prop.get("multi_select", [])]
            
        def get_number(prop: Dict[str, Any]) -> float:
            return float(prop.get("number", 0))
            
        def get_date(prop: Dict[str, Any]) -> Optional[datetime]:
            date_str = prop.get("date", {}).get("start")
            return datetime.fromisoformat(date_str) if date_str else None
            
        return {
            "id": page["id"],
            "title": get_title(props["Title"]),
            "description": get_rich_text(props["Description"]),
            "creator": get_rich_text(props["Creator"]),
            "status": get_select(props["Status"]),
            "priority_score": get_number(props["Priority Score"]),
            "innovation_category": get_select(props["Innovation Category"]),
            "market_size": get_rich_text(props["Market Size"]),
            "market_analysis": get_rich_text(props["Market Analysis"]),
            "ai_insights": get_rich_text(props["AI Insights"]),
            "competitive_advantage": get_rich_text(props["Competitive Advantage"]),
            
            "impact_metrics": {
                "potential_users": int(get_number(props["Potential Users"])),
                "regions_affected": get_multi_select(props["Regions Affected"]),
                "sdg_goals": get_multi_select(props["SDG Goals"]),
                "environmental_impact": get_select(props["Environmental Impact"]),
                "social_impact": get_select(props["Social Impact"]),
                "economic_impact": get_select(props["Economic Impact"])
            },
            
            "implementation": {
                "current_stage": get_select(props["Current Stage"]),
                "tech_stack": get_multi_select(props["Tech Stack"]),
                "resource_requirements": get_multi_select(props["Resource Requirements"]),
                "development_stages": get_multi_select(props["Development Stages"]),
                "challenges": get_multi_select(props["Challenges"]),
                "solutions": get_multi_select(props["Solutions"])
            },
            
            "improvement_suggestions": get_multi_select(props["Improvement Suggestions"]),
            "next_steps": get_multi_select(props["Next Steps"]),
            
            "created_at": get_date(props["Created At"]),
            "updated_at": get_date(props.get("Updated At", {}))
        }
        
    def _convert_to_notion_properties(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Python dict to Notion properties format."""
        properties = {}
        
        # Map fields to Notion property types
        if "title" in data:
            properties["Name"] = {"title": [{"text": {"content": data["title"]}}]}
            
        if "description" in data:
            properties["Description"] = {"rich_text": [{"text": {"content": data["description"]}}]}
            
        if "status" in data:
            properties["Status"] = {"select": {"name": data["status"]}}
            
        if "priority_score" in data:
            properties["Priority Score"] = {"number": data["priority_score"]}
            
        if "innovation_category" in data:
            properties["Category"] = {"select": {"name": data["innovation_category"]}}
            
        if "tags" in data:
            properties["Tags"] = {"multi_select": [{"name": tag} for tag in data["tags"]]}
            
        if "impact_metrics" in data:
            metrics = data["impact_metrics"]
            properties["Potential Users"] = {"number": metrics["potential_users"]}
            properties["Regions"] = {"multi_select": [{"name": region} for region in metrics["regions_affected"]]}
            properties["SDG Goals"] = {"multi_select": [{"name": goal} for goal in metrics["sdg_goals"]]}
            
        if "implementation" in data:
            impl = data["implementation"]
            properties["Current Stage"] = {"select": {"name": impl["current_stage"]}}
            properties["Tech Stack"] = {"multi_select": [{"name": tech} for tech in impl["tech_stack"]]}
            
        return properties
        
    def _convert_from_notion(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Notion page to Python dict format."""
        props = page["properties"]
        data = {
            "id": page["id"],
            "title": self._get_title(props.get("Name", {})),
            "description": self._get_text(props.get("Description", {})),
            "status": self._get_select(props.get("Status", {})),
            "priority_score": self._get_number(props.get("Priority Score", {})),
            "innovation_category": self._get_select(props.get("Category", {})),
            "tags": self._get_multi_select(props.get("Tags", {})),
            
            "impact_metrics": {
                "potential_users": self._get_number(props.get("Potential Users", {})),
                "regions_affected": self._get_multi_select(props.get("Regions", {})),
                "sdg_goals": self._get_multi_select(props.get("SDG Goals", {}))
            },
            
            "implementation": {
                "current_stage": self._get_select(props.get("Current Stage", {})),
                "tech_stack": self._get_multi_select(props.get("Tech Stack", {}))
            }
        }
        
        return {k: v for k, v in data.items() if v is not None}
        
    def _get_title(self, prop: Dict[str, Any]) -> Optional[str]:
        """Extract title from Notion property."""
        try:
            return prop["title"][0]["text"]["content"]
        except (KeyError, IndexError):
            return None
            
    def _get_text(self, prop: Dict[str, Any]) -> Optional[str]:
        """Extract text from Notion property."""
        try:
            return prop["rich_text"][0]["text"]["content"]
        except (KeyError, IndexError):
            return None
            
    def _get_select(self, prop: Dict[str, Any]) -> Optional[str]:
        """Extract select value from Notion property."""
        try:
            return prop["select"]["name"]
        except KeyError:
            return None
            
    def _get_multi_select(self, prop: Dict[str, Any]) -> List[str]:
        """Extract multi-select values from Notion property."""
        try:
            return [item["name"] for item in prop["multi_select"]]
        except KeyError:
            return []
            
    def _get_number(self, prop: Dict[str, Any]) -> Optional[float]:
        """Extract number from Notion property."""
        try:
            return prop["number"]
        except KeyError:
            return None 
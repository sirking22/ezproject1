from typing import Dict, Any, List, Optional
from datetime import datetime
from .date_utils import format_notion_date, parse_notion_date

def create_title_property(text: str) -> Dict[str, Any]:
    """Create a title property."""
    return {
        "title": [{"text": {"content": text}}]
    }

def create_rich_text_property(text: Optional[str]) -> Dict[str, Any]:
    """Create a rich text property."""
    if not text:
        return {"rich_text": []}
    return {
        "rich_text": [{"text": {"content": text}}]
    }

def create_select_property(name: str) -> Dict[str, Any]:
    """Create a select property."""
    return {
        "select": {"name": name}
    }

def create_multi_select_property(names: List[str]) -> Dict[str, Any]:
    """Create a multi-select property."""
    return {
        "multi_select": [{"name": name} for name in names]
    }

def create_date_property(date: Optional[datetime]) -> Dict[str, Any]:
    """Create a date property."""
    date_str = format_notion_date(date)
    if not date_str:
        return {"date": None}
    return {
        "date": {"start": date_str}
    }

def create_number_property(number: int) -> Dict[str, Any]:
    """Create a number property."""
    return {
        "number": number
    }

def extract_title(props: Dict[str, Any], key: str) -> Optional[str]:
    """Extract title from properties."""
    if key not in props or not props[key].get("title"):
        return None
    return props[key]["title"][0]["text"]["content"]

def extract_rich_text(props: Dict[str, Any], key: str) -> Optional[str]:
    """Extract rich text from properties."""
    if key not in props or not props[key].get("rich_text"):
        return None
    return props[key]["rich_text"][0]["text"]["content"]

def extract_select(props: Dict[str, Any], key: str) -> Optional[str]:
    """Extract select from properties."""
    if key not in props or not props[key].get("select"):
        return None
    return props[key]["select"]["name"]

def extract_multi_select(props: Dict[str, Any], key: str) -> List[str]:
    """Extract multi-select from properties."""
    if key not in props or not props[key].get("multi_select"):
        return []
    return [item["name"] for item in props[key]["multi_select"]]

def extract_date(props: Dict[str, Any], key: str) -> Optional[datetime]:
    """Extract datetime from a Notion date property"""
    if key not in props or not props[key].get("date"):
        return None
    date_str = props[key]["date"].get("start")
    return parse_notion_date(date_str) if date_str else None

def extract_number(props: Dict[str, Any], key: str) -> Optional[int]:
    """Extract number from properties."""
    if key not in props or props[key].get("number") is None:
        return None
    return int(props[key]["number"]) 
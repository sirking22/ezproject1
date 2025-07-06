"""Pydantic models for Notion API data structures."""
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field


class NotionBlock(BaseModel):
    """Base class for Notion blocks."""
    id: str
    type: str
    created_time: datetime
    last_edited_time: datetime
    has_children: bool = False
    archived: bool = False


class TextBlock(NotionBlock):
    """Text block in Notion."""
    type: str = "paragraph"
    paragraph: Dict[str, Any] = Field(default_factory=dict)


class TodoBlock(NotionBlock):
    """Todo block in Notion."""
    type: str = "to_do"
    to_do: Dict[str, Any] = Field(default_factory=dict)
    checked: bool = False


class HeadingBlock(NotionBlock):
    """Heading block in Notion."""
    type: str = Field(..., pattern="^heading_[1-3]$")
    heading_1: Optional[Dict[str, Any]] = None
    heading_2: Optional[Dict[str, Any]] = None
    heading_3: Optional[Dict[str, Any]] = None


class NotionProperty(BaseModel):
    """Base class for Notion properties."""
    id: str
    type: str


class TitleProperty(NotionProperty):
    """Title property in Notion."""
    type: str = "title"
    title: List[Dict[str, Any]] = Field(default_factory=list)


class SelectProperty(NotionProperty):
    """Select property in Notion."""
    type: str = "select"
    select: Dict[str, Any] = Field(default_factory=dict)


class DateProperty(NotionProperty):
    """Date property in Notion."""
    type: str = "date"
    date: Optional[Dict[str, Any]] = None


class PeopleProperty(NotionProperty):
    """People property in Notion."""
    type: str = "people"
    people: List[Dict[str, Any]] = Field(default_factory=list)


class NumberProperty(NotionProperty):
    """Number property in Notion."""
    type: str = "number"
    number: Optional[float] = None


class UrlProperty(NotionProperty):
    """URL property in Notion."""
    type: str = "url"
    url: Optional[str] = None


class NotionPage(BaseModel):
    """Notion page model."""
    id: str
    created_time: datetime
    last_edited_time: datetime
    archived: bool = False
    properties: Dict[str, Union[
        TitleProperty,
        SelectProperty,
        DateProperty,
        PeopleProperty,
        NumberProperty,
        UrlProperty
    ]] = Field(default_factory=dict)


class NotionDatabase(BaseModel):
    """Notion database model."""
    id: str
    created_time: datetime
    last_edited_time: datetime
    title: List[Dict[str, Any]] = Field(default_factory=list)
    properties: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    archived: bool = False 
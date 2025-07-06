"""Base models for the application."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class User(BaseModel):
    """User model for authentication and settings"""
    id: str
    telegram_id: Optional[int] = None
    notion_token: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    settings: Dict[str, Any] = Field(default_factory=dict)

@dataclass
class TaskDTO:
    """Data transfer object for tasks."""
    
    id: str
    title: str
    status: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class LearningProgressDTO:
    """Data transfer object for learning progress."""
    
    task_id: str
    topic: str
    status: str
    completion_rate: int
    last_review: datetime
    next_review: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class Task(BaseModel):
    """Task model representing a learning task or item"""
    id: str
    title: str
    description: Optional[str] = None
    status: str = "Not Started"
    due_date: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    priority: str = "Medium"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    time_estimate: Optional[int] = None  # in minutes
    actual_time: Optional[int] = None  # in minutes
    
    def update_status(self, new_status: str) -> None:
        """Update task status and related timestamps"""
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        if new_status == "Completed" and not self.completed_at:
            self.completed_at = datetime.utcnow()
        elif new_status == "Cancelled" and not self.cancelled_at:
            self.cancelled_at = datetime.utcnow()

class NotionTask(BaseModel):
    """Task model for Notion integration."""
    
    id: str
    title: str
    status: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
    def update_status(self, new_status: str) -> None:
        """Update task status and related timestamps."""
        if new_status != self.status:
            self.status = new_status
            self.updated_at = datetime.now()
            
    def to_dto(self) -> TaskDTO:
        """Convert to DTO."""
        return TaskDTO(
            id=self.id,
            title=self.title,
            status=self.status,
            description=self.description,
            due_date=self.due_date,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

class NotionLearningProgress(BaseModel):
    """Learning progress model for Notion integration."""
    
    task_id: str
    topic: str
    status: str
    completion_rate: int
    last_review: datetime
    next_review: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
    def update_progress(self, completion_rate: int) -> None:
        """Update progress and related timestamps."""
        if completion_rate != self.completion_rate:
            self.completion_rate = completion_rate
            self.updated_at = datetime.now()
            
    def to_dto(self) -> LearningProgressDTO:
        """Convert to DTO."""
        return LearningProgressDTO(
            task_id=self.task_id,
            topic=self.topic,
            status=self.status,
            completion_rate=self.completion_rate,
            last_review=self.last_review,
            next_review=self.next_review,
            notes=self.notes,
            created_at=self.created_at,
            updated_at=self.updated_at
        ) 
from sqlalchemy import Column, String, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from .base import BaseModel

class Project(BaseModel):
    __tablename__ = "projects"

    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="active")
    
    # Отношения
    epics = relationship("Epic", back_populates="project", cascade="all, delete-orphan")

class Epic(BaseModel):
    __tablename__ = "epics"

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="planning")
    
    # Отношения
    project = relationship("Project", back_populates="epics")
    tasks = relationship("Task", back_populates="epic", cascade="all, delete-orphan")

class Task(BaseModel):
    __tablename__ = "tasks"

    epic_id = Column(Integer, ForeignKey("epics.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="todo")
    priority = Column(String(20), default="medium")
    assigned_to = Column(Integer, ForeignKey("employees.id"), nullable=True)
    
    # Отношения
    epic = relationship("Epic", back_populates="tasks")
    assignee = relationship("Employee", back_populates="assigned_tasks") 
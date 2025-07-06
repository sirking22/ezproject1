from sqlalchemy import Column, String, Text, Table, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel, Base

# Таблица для связи идей и тегов
idea_tags = Table(
    'idea_tags',
    Base.metadata,
    Column('idea_id', Integer, ForeignKey('ideas.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class Idea(BaseModel):
    __tablename__ = "ideas"

    title = Column(String(255), nullable=False)
    description = Column(Text)
    ai_enhanced_content = Column(Text)
    status = Column(String(50), default="draft")
    
    # Отношения
    tags = relationship("Tag", secondary=idea_tags, back_populates="ideas")

class Tag(BaseModel):
    __tablename__ = "tags"

    name = Column(String(50), unique=True, nullable=False)
    
    # Отношения
    ideas = relationship("Idea", secondary=idea_tags, back_populates="tags") 
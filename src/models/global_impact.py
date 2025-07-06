"""Models for storing global impact idea data."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class ImpactMetrics(BaseModel):
    """Impact metrics for an idea."""
    
    potential_users: int = Field(
        description="Estimated number of potential users",
        default=0
    )
    regions_affected: List[str] = Field(
        description="Geographic regions that could benefit",
        default_factory=list
    )
    sdg_goals: List[str] = Field(
        description="UN Sustainable Development Goals addressed",
        default_factory=list
    )
    environmental_impact: str = Field(
        description="Environmental impact assessment",
        default="medium"
    )
    social_impact: str = Field(
        description="Social impact assessment",
        default="medium"
    )
    economic_impact: str = Field(
        description="Economic impact assessment",
        default="medium"
    )

class Implementation(BaseModel):
    """Implementation details for an idea."""
    
    current_stage: str = Field(
        description="Current development stage",
        default="concept"
    )
    tech_stack: List[str] = Field(
        description="Required technologies",
        default_factory=list
    )
    resource_requirements: List[str] = Field(
        description="Required resources",
        default_factory=list
    )
    development_stages: List[str] = Field(
        description="Planned development stages",
        default_factory=list
    )
    challenges: List[str] = Field(
        description="Known challenges",
        default_factory=list
    )
    solutions: List[str] = Field(
        description="Proposed solutions to challenges",
        default_factory=list
    )

class GlobalImpactIdea(BaseModel):
    """Model for storing global impact idea data."""
    
    id: str = Field(description="Unique identifier")
    title: str = Field(description="Idea title")
    description: str = Field(description="Detailed description")
    creator: str = Field(description="Creator identifier")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: Optional[datetime] = Field(
        description="Last update timestamp",
        default=None
    )
    
    # Impact assessment
    impact_metrics: ImpactMetrics = Field(
        description="Impact metrics and assessments",
        default_factory=ImpactMetrics
    )
    
    # Implementation details
    implementation: Implementation = Field(
        description="Implementation details and progress",
        default_factory=Implementation
    )
    
    # Analysis and insights
    innovation_category: str = Field(
        description="Type of innovation",
        default="product"
    )
    competitive_advantage: str = Field(
        description="Unique value proposition",
        default=""
    )
    market_size: str = Field(
        description="Total addressable market size",
        default=""
    )
    market_analysis: str = Field(
        description="Market potential analysis",
        default=""
    )
    
    # Status and priority
    status: str = Field(
        description="Current status",
        default="active"
    )
    priority_score: float = Field(
        description="Priority score (0-10)",
        default=1.0
    )
    
    # AI-generated content
    ai_insights: str = Field(
        description="AI-generated insights",
        default=""
    )
    improvement_suggestions: List[str] = Field(
        description="AI-suggested improvements",
        default_factory=list
    )
    next_steps: List[str] = Field(
        description="Recommended next steps",
        default_factory=list
    )
    
    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 
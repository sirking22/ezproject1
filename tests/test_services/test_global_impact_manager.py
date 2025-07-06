"""Tests for GlobalImpactManager service."""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock

from src.models.global_impact import GlobalImpactIdea
from src.services.global_impact_manager import GlobalImpactManager

pytestmark = pytest.mark.asyncio

async def test_create_impact_idea(impact_manager: GlobalImpactManager, sample_idea_data: dict):
    """Test creating a new impact idea."""
    # Setup
    impact_manager.notion_repo.create_idea = AsyncMock(return_value=sample_idea_data)
    
    # Execute
    idea = await impact_manager.create_impact_idea(sample_idea_data)
    
    # Assert
    assert isinstance(idea, GlobalImpactIdea)
    assert idea.title == sample_idea_data["title"]
    assert idea.description == sample_idea_data["description"]
    assert idea.creator == sample_idea_data["creator"]
    
    # Verify AI analysis was called
    impact_manager.llm_service.analyze_impact.assert_called_once()
    impact_manager.llm_service.analyze_market.assert_called_once()
    impact_manager.llm_service.analyze_tech_requirements.assert_called_once()
    impact_manager.llm_service.generate_suggestions.assert_called_once()
    impact_manager.llm_service.generate_analysis.assert_called_once()
    
    # Verify Notion storage was called
    impact_manager.notion_repo.create_idea.assert_called_once()

async def test_get_idea(impact_manager: GlobalImpactManager, sample_idea_data: dict):
    """Test retrieving an idea by ID."""
    # Setup
    idea_id = "test_id"
    impact_manager.notion_repo.get_idea = AsyncMock(return_value=sample_idea_data)
    
    # Execute
    idea = await impact_manager.get_idea(idea_id)
    
    # Assert
    assert isinstance(idea, GlobalImpactIdea)
    assert idea.title == sample_idea_data["title"]
    assert idea.description == sample_idea_data["description"]
    
    # Verify Notion retrieval was called
    impact_manager.notion_repo.get_idea.assert_called_once_with(idea_id)

async def test_get_idea_not_found(impact_manager: GlobalImpactManager):
    """Test retrieving a non-existent idea."""
    # Setup
    idea_id = "non_existent_id"
    impact_manager.notion_repo.get_idea = AsyncMock(return_value=None)
    
    # Execute
    idea = await impact_manager.get_idea(idea_id)
    
    # Assert
    assert idea is None
    
    # Verify Notion retrieval was called
    impact_manager.notion_repo.get_idea.assert_called_once_with(idea_id)

async def test_get_priority_ideas(impact_manager: GlobalImpactManager, sample_idea_data: dict):
    """Test retrieving priority-sorted ideas."""
    # Setup
    ideas_data = [sample_idea_data, sample_idea_data]
    impact_manager.notion_repo.get_ideas = AsyncMock(return_value=ideas_data)
    
    # Execute
    ideas = await impact_manager.get_priority_ideas(limit=2)
    
    # Assert
    assert len(ideas) == 2
    assert all(isinstance(idea, GlobalImpactIdea) for idea in ideas)
    
    # Verify Notion query was called
    impact_manager.notion_repo.get_ideas.assert_called_once_with(
        sort_by="priority_score",
        limit=2
    )

async def test_analyze_global_trends(impact_manager: GlobalImpactManager, sample_idea_data: dict):
    """Test analyzing global trends."""
    # Setup
    ideas_data = [sample_idea_data, sample_idea_data]
    impact_manager.notion_repo.get_ideas = AsyncMock(return_value=ideas_data)
    impact_manager.llm_service.generate_analysis = AsyncMock(return_value="""
    Category 1: 5
    Category 2: 3
    
    Distribution analysis
    
    - Resource 1
    - Resource 2
    
    - Pattern 1
    - Pattern 2
    
    - Area 1
    - Area 2
    
    - Opportunity 1
    - Opportunity 2
    """)
    
    # Execute
    trends = await impact_manager.analyze_global_trends()
    
    # Assert
    assert isinstance(trends, dict)
    assert "top_categories" in trends
    assert "impact_distribution" in trends
    assert "resource_requirements" in trends
    assert "success_patterns" in trends
    assert "improvement_areas" in trends
    assert "collaboration_opportunities" in trends
    
    # Verify data structure
    assert isinstance(trends["top_categories"], dict)
    assert isinstance(trends["impact_distribution"], str)
    assert isinstance(trends["resource_requirements"], list)
    assert isinstance(trends["success_patterns"], list)
    assert isinstance(trends["improvement_areas"], list)
    assert isinstance(trends["collaboration_opportunities"], list)
    
    # Verify Notion query was called
    impact_manager.notion_repo.get_ideas.assert_called_once_with(limit=100)
    
    # Verify LLM analysis was called
    impact_manager.llm_service.generate_analysis.assert_called_once()

def test_calculate_priority_score(impact_manager: GlobalImpactManager):
    """Test priority score calculation."""
    # Setup
    impact_analysis = {
        "user_estimate": 5000000,  # 5M users
        "affected_regions": ["North America", "Europe", "Asia"],
        "relevant_sdgs": ["No Poverty", "Quality Education"],
        "environmental_assessment": "high",
        "social_assessment": "medium",
        "economic_assessment": "high"
    }
    
    # Execute
    score = impact_manager._calculate_priority_score(impact_analysis)
    
    # Assert
    assert isinstance(score, float)
    assert 0 <= score <= 10  # Score should be normalized
    
    # Test edge cases
    zero_impact = {
        "user_estimate": 0,
        "affected_regions": [],
        "relevant_sdgs": [],
        "environmental_assessment": "low",
        "social_assessment": "low",
        "economic_assessment": "low"
    }
    min_score = impact_manager._calculate_priority_score(zero_impact)
    assert min_score > 0  # Should have a minimum score
    
    max_impact = {
        "user_estimate": 10000000,  # 10M+ users
        "affected_regions": ["Global"],
        "relevant_sdgs": ["No Poverty", "Zero Hunger", "Quality Education"],
        "environmental_assessment": "high",
        "social_assessment": "high",
        "economic_assessment": "high"
    }
    max_score = impact_manager._calculate_priority_score(max_impact)
    assert max_score <= 10  # Should be capped at 10 
"""setup_notion_databases.py

Скрипт создаёт в Notion все базы .life и добавляет в каждую тестовую запись
с текстовыми плейсхолдерами для формул и relation-полей.

Требуется переменные окружения:
- NOTION_TOKEN — интеграционный токен Notion
- NOTION_PARENT_PAGE_ID — ID страницы/рабочей области, в которой будут созданы базы

Запуск:
    python scripts/setup_notion_databases.py
"""
from __future__ import annotations

import os
from typing import Dict, List
from notion_client import Client

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_client() -> Client:
    token = os.getenv("NOTION_TOKEN")
    assert token, "NOTION_TOKEN env var is required"
    return Client(auth=token)


def create_database(client: Client, parent_page_id: str, title: str, properties: Dict) -> str:
    """Create a Notion database and return its ID."""
    response = client.databases.create(
        parent={"type": "page_id", "page_id": parent_page_id},
        title=[{"type": "text", "text": {"content": title}}],
        properties=properties,
    )
    return response["id"]


def add_sample_row(client: Client, database_id: str, sample_properties: Dict):
    client.pages.create(parent={"database_id": database_id}, properties=sample_properties)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

def make_text_prop(name: str) -> Dict:
    return {name: {"title": {}}}


def make_number_prop(name: str) -> Dict:
    return {name: {"number": {}}}


def make_select_prop(name: str, options: List[str]) -> Dict:
    return {
        name: {
            "select": {
                "options": [{"name": v, "color": "default"} for v in options]
            }
        }
    }


def make_multi_select_prop(name: str, options: List[str]) -> Dict:
    return {
        name: {
            "multi_select": {
                "options": [{"name": v, "color": "default"} for v in options]
            }
        }
    }


def make_date_prop(name: str) -> Dict:
    return {name: {"date": {}}}

# ---------------------------------------------------------------------------
# Database definitions (shortened to essentials)
# ---------------------------------------------------------------------------

db_definitions = {
    "Habit / Skill Tracker": {
        "properties": {
            **make_text_prop("habit_name"),
            **make_text_prop("description"),
            **make_number_prop("current_streak"),
            **make_number_prop("total_completions"),
            **make_text_prop("skill_level"),
            **make_date_prop("last_review"),
            **make_text_prop("related_rituals"),  # relation placeholder
            **make_text_prop("insights"),
            **make_text_prop("experiment_notes"),
            **make_multi_select_prop("tags", [
                "habit",
                "skill",
                "focus",
                "energy",
                "ritual",
                "experiment",
            ]),
            **make_text_prop("formula_streak_score"),
            **make_text_prop("related_tasks"),
            **make_select_prop("priority", ["low", "medium", "high", "critical"]),
        },
        "sample": {
            "habit_name": {"title": [{"text": {"content": "Утренняя медитация"}}]},
            "description": {"rich_text": [{"text": {"content": "10-минутная сессия"}}]},
            "current_streak": {"number": 3},
            "total_completions": {"number": 15},
            "skill_level": {"rich_text": [{"text": {"content": "beginner"}}]},
            "formula_streak_score": {"rich_text": [{"text": {"content": "=current_streak * total_completions / 30"}}]},
            "related_rituals": {"rich_text": [{"text": {"content": "Утренний ритуал"}}]},
            "priority": {"select": {"name": "high"}},
        },
    },
    "Rituals": {
        "properties": {
            **make_text_prop("ritual_name"),
            **make_text_prop("description"),
            **make_text_prop("habits_list"),
            **make_select_prop("status", ["active", "paused", "archived"]),
            **make_number_prop("current_streak"),
            **make_number_prop("total_completions"),
            **make_date_prop("last_completed"),
            **make_text_prop("related_tasks"),
            **make_text_prop("insights"),
            **make_text_prop("formula_completion_rate"),
            **make_multi_select_prop("tags", ["morning", "evening", "focus", "energy"]),
            **make_select_prop("priority", ["low", "medium", "high", "critical"]),
        },
        "sample": {
            "ritual_name": {"title": [{"text": {"content": "Утренний ритуал"}}]},
            "description": {"rich_text": [{"text": {"content": "Запуск дня с фокусом и энергией"}}]},
            "habits_list": {"rich_text": [{"text": {"content": "Утренняя медитация, Планирование дня"}}]},
            "status": {"select": {"name": "active"}},
            "formula_completion_rate": {"rich_text": [{"text": {"content": "=total_completions / days_tracked"}}]},
            "priority": {"select": {"name": "medium"}},
        },
    },
    "Experience Hub": {
        "properties": {
            **make_date_prop("date"),
            **make_select_prop("source", ["personal", "agent", "team", "external"]),
            **make_text_prop("author"),
            **make_text_prop("insight"),
            **make_text_prop("context"),
            **make_select_prop("impact", ["low", "medium", "high"]),
            **make_select_prop("type", ["insight", "pattern", "anti-pattern", "error"]),
            **make_text_prop("related_projects"),
            **make_text_prop("related_agents"),
            **make_text_prop("related_tasks"),
            **make_text_prop("related_materials"),
            **make_multi_select_prop("tags", ["workflow", "automation", "learning", "fail", "pattern"]),
            **make_text_prop("implementation_note"),
            **make_select_prop("status", ["raw", "reviewed", "standardized", "archived"]),
            **make_number_prop("success_count"),
            **make_text_prop("formula_impact_score"),
            **make_select_prop("priority", ["low", "medium", "high", "critical"]),
            **make_text_prop("reviewed_by"),
            **make_date_prop("review_date"),
            **make_select_prop("actionable", ["yes", "no"]),
            **make_text_prop("review_notes"),
        },
        "sample": {
            "date": {"date": {"start": "2025-07-01"}},
            "source": {"select": {"name": "personal"}},
            "author": {"rich_text": [{"text": {"content": "Я"}}]},
            "insight": {"title": [{"text": {"content": "Утренняя медитация повышает фокус"}}]},
            "impact": {"select": {"name": "high"}},
            "type": {"select": {"name": "insight"}},
            "status": {"select": {"name": "raw"}},
            "formula_impact_score": {"rich_text": [{"text": {"content": "=success_count * 3"}}]},
            "priority": {"select": {"name": "high"}},
        },
    },
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    client = get_client()
    parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID")
    assert parent_page_id, "NOTION_PARENT_PAGE_ID env var is required"

    for title, spec in db_definitions.items():
        print(f"Creating database: {title} …", end=" ")
        db_id = create_database(client, parent_page_id, title, spec["properties"])
        add_sample_row(client, db_id, spec["sample"])
        print("✓")

    print("Done. Databases created with sample rows.")


if __name__ == "__main__":
    main() 
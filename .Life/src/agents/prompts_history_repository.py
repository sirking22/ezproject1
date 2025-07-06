import json
from typing import List, Optional, Dict, Any
from pathlib import Path

HISTORY_PATH = Path(__file__).parent / "prompts_history.json"

class AgentPromptHistoryRepository:
    @staticmethod
    def add_history(record: Dict[str, Any]) -> None:
        history = AgentPromptHistoryRepository.get_all_history()
        history.append(record)
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    @staticmethod
    def get_history_by_agent(agent_id: str) -> List[Dict[str, Any]]:
        history = AgentPromptHistoryRepository.get_all_history()
        return [h for h in history if h["agent_id"] == agent_id]

    @staticmethod
    def get_all_history() -> List[Dict[str, Any]]:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f) 
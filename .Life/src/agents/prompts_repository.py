import json
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
from .prompts_history_repository import AgentPromptHistoryRepository

PROMPTS_PATH = Path(__file__).parent / "prompts.json"

class AgentPromptRepository:
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        with open(PROMPTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def get_by_id(agent_id: str) -> Optional[Dict[str, Any]]:
        prompts = AgentPromptRepository.get_all()
        for prompt in prompts:
            if prompt["agent_id"] == agent_id:
                return prompt
        return None

    @staticmethod
    def add(prompt: Dict[str, Any], author: str = "system") -> None:
        prompts = AgentPromptRepository.get_all()
        prompt["meta"]["version"] = 1
        prompt["meta"]["updated"] = datetime.utcnow().isoformat() + "Z"
        prompts.append(prompt)
        with open(PROMPTS_PATH, "w", encoding="utf-8") as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)
        AgentPromptHistoryRepository.add_history({
            "agent_id": prompt["agent_id"],
            "timestamp": prompt["meta"]["updated"],
            "action": "create",
            "old_prompt": None,
            "new_prompt": prompt["prompt"],
            "meta": {"author": author}
        })

    @staticmethod
    def update(agent_id: str, new_prompt: Dict[str, Any], author: str = "system") -> bool:
        prompts = AgentPromptRepository.get_all()
        for i, prompt in enumerate(prompts):
            if prompt["agent_id"] == agent_id:
                old_prompt = prompt["prompt"]
                new_version = prompt["meta"].get("version", 1) + 1
                new_prompt["meta"]["version"] = new_version
                new_prompt["meta"]["updated"] = datetime.utcnow().isoformat() + "Z"
                prompts[i] = new_prompt
                with open(PROMPTS_PATH, "w", encoding="utf-8") as f:
                    json.dump(prompts, f, ensure_ascii=False, indent=2)
                AgentPromptHistoryRepository.add_history({
                    "agent_id": agent_id,
                    "timestamp": new_prompt["meta"]["updated"],
                    "action": "update",
                    "old_prompt": old_prompt,
                    "new_prompt": new_prompt["prompt"],
                    "meta": {"author": author}
                })
                return True
        return False

    @staticmethod
    def delete(agent_id: str, author: str = "system") -> bool:
        prompts = AgentPromptRepository.get_all()
        new_prompts = [p for p in prompts if p["agent_id"] != agent_id]
        if len(new_prompts) == len(prompts):
            return False
        with open(PROMPTS_PATH, "w", encoding="utf-8") as f:
            json.dump(new_prompts, f, ensure_ascii=False, indent=2)
        AgentPromptHistoryRepository.add_history({
            "agent_id": agent_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": "delete",
            "old_prompt": AgentPromptRepository.get_by_id(agent_id),
            "new_prompt": None,
            "meta": {"author": author}
        })
        return True

    @staticmethod
    def restore_version(agent_id: str, version: int, author: str = "system") -> bool:
        history = AgentPromptHistoryRepository.get_history_by_agent(agent_id)
        for record in reversed(history):
            if record["action"] in ("create", "update") and record["meta"].get("version") == version:
                prompt = AgentPromptRepository.get_by_id(agent_id)
                if not prompt:
                    return False
                prompt["prompt"] = record["new_prompt"]
                prompt["meta"]["version"] = version
                prompt["meta"]["updated"] = datetime.utcnow().isoformat() + "Z"
                AgentPromptRepository.update(agent_id, prompt, author=author)
                return True
        return False 
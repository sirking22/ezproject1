import json
from typing import List, Dict, Any, Optional
from pathlib import Path

LOG_PATH = Path(__file__).parent / "meta_feedback_log.json"

class MetaFeedbackLogRepository:
    @staticmethod
    def add_log(record: Dict[str, Any]) -> None:
        logs = MetaFeedbackLogRepository.get_logs()
        logs.append(record)
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

    @staticmethod
    def get_logs() -> List[Dict[str, Any]]:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def get_logs_by_topic(topic: str) -> List[Dict[str, Any]]:
        logs = MetaFeedbackLogRepository.get_logs()
        return [log for log in logs if log["topic"] == topic]

    @staticmethod
    def get_logs_by_person(person: str) -> List[Dict[str, Any]]:
        logs = MetaFeedbackLogRepository.get_logs()
        return [log for log in logs if log["from"] == person or log["to"] == person] 
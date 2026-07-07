import json
from datetime import datetime
from config import HISTORY_FILE
from utils.logger import logger
from typing import List, Dict

class HistoryManager:
    @staticmethod
    def _load_history() -> List[Dict]:
        if not HISTORY_FILE.exists():
            return []
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error("History file is corrupted. Starting fresh.")
            return []
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            return []

    @staticmethod
    def _save_history(data: List[Dict]):
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

    @staticmethod
    def add_entry(version: str, count: int, duration: float, export_loc: str = "None"):
        history = HistoryManager._load_history()
        entry = {
            "timestamp": datetime.now().isoformat(),
            "version": version,
            "count": count,
            "duration": round(duration, 4),
            "export_location": export_loc
        }
        history.append(entry)
        HistoryManager._save_history(history)
        logger.debug("Added entry to history.")

    @staticmethod
    def get_history() -> List[Dict]:
        return HistoryManager._load_history()

    @staticmethod
    def clear_history():
        HistoryManager._save_history([])
        logger.info("History cleared.")

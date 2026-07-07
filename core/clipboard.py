import pyperclip
from typing import List
from utils.logger import logger

class ClipboardManager:
    @staticmethod
    def copy_to_clipboard(text: str) -> bool:
        try:
            pyperclip.copy(text)
            logger.info("Successfully copied to clipboard.")
            return True
        except Exception as e:
            logger.error(f"Failed to copy to clipboard: {e}")
            return False

    @staticmethod
    def copy_list_to_clipboard(items: List[str]) -> bool:
        # For large lists, it might take a moment.
        text = "\n".join(items)
        return ClipboardManager.copy_to_clipboard(text)

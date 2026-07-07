import uuid
from typing import List, Tuple, Dict
from utils.logger import logger

class UUIDValidator:
    @staticmethod
    def validate_uuid(val: str) -> bool:
        try:
            uuid_obj = uuid.UUID(val)
            return str(uuid_obj) == val.lower()
        except ValueError:
            return False

    @staticmethod
    def validate_list(uuids: List[str]) -> Dict[str, any]:
        """Validates a list of UUIDs, finds duplicates, and separates them."""
        logger.info(f"Validating {len(uuids)} items...")
        valid = []
        invalid = []
        duplicates = set()
        seen = set()

        for u in uuids:
            u_clean = u.strip()
            if not UUIDValidator.validate_uuid(u_clean):
                invalid.append(u_clean)
                continue
            
            if u_clean in seen:
                duplicates.add(u_clean)
            else:
                seen.add(u_clean)
                valid.append(u_clean)

        logger.info(f"Validation complete: {len(valid)} valid, {len(invalid)} invalid, {len(duplicates)} duplicates.")
        return {
            "valid": valid,
            "invalid": invalid,
            "duplicates": list(duplicates)
        }

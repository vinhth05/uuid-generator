import pytest
import uuid
from core.validator import UUIDValidator

def test_validate_valid_uuid():
    valid_uuid = str(uuid.uuid4())
    assert UUIDValidator.validate_uuid(valid_uuid) is True

def test_validate_invalid_uuid():
    assert UUIDValidator.validate_uuid("invalid-uuid-string") is False
    assert UUIDValidator.validate_uuid("123e4567-e89b-12d3-a456-426614174000x") is False

def test_validate_list():
    u1 = str(uuid.uuid4())
    u2 = str(uuid.uuid4())
    
    test_list = [u1, u2, u1, "invalid1"]
    
    result = UUIDValidator.validate_list(test_list)
    
    assert len(result["valid"]) == 2
    assert u1 in result["valid"]
    assert u2 in result["valid"]
    
    assert len(result["duplicates"]) == 1
    assert u1 in result["duplicates"]
    
    assert len(result["invalid"]) == 1
    assert "invalid1" in result["invalid"]

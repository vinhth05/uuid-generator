import pytest
import queue
import time
from core.generator import UUIDGenerator

def test_generate_v4():
    generator = UUIDGenerator()
    q = queue.Queue()
    
    def progress(c, t): pass
    def complete(cancelled): pass
    
    # Run synchronously for test by calling worker directly
    generator.generate_worker("4", 100, "DNS", "", q, progress, complete)
    
    results = []
    while not q.empty():
        results.extend(q.get())
        
    assert len(results) == 100
    assert len(set(results)) == 100  # Unique

def test_generate_v3_namespace():
    generator = UUIDGenerator()
    q = queue.Queue()
    
    def progress(c, t): pass
    def complete(cancelled): pass
    
    generator.generate_worker("3", 10, "DNS", "test.com", q, progress, complete)
    
    results = []
    while not q.empty():
        results.extend(q.get())
        
    assert len(results) == 10
    # v3 is deterministic for the same namespace/name, so all 10 should be identical
    assert len(set(results)) == 1

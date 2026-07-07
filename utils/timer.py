import time
from functools import wraps
from utils.logger import logger

class Timer:
    def __init__(self, name="Timer"):
        self.name = name
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        self.duration = self.end_time - self.start_time
        logger.debug(f"{self.name} took {self.duration:.4f} seconds.")

def time_it(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logger.debug(f"Function {func.__name__} took {end - start:.4f} seconds.")
        return result
    return wrapper

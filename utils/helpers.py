import re
from datetime import datetime

def sanitize_filename(filename: str) -> str:
    """Sanitize string to be safe for filenames."""
    # Remove invalid characters
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Replace spaces with underscores
    filename = filename.replace(" ", "_")
    return filename

def generate_export_filename(prefix="uuid") -> str:
    """Generate a default export filename based on timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}"

def format_number(num: int) -> str:
    """Format large numbers with commas."""
    return f"{num:,}"

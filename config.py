import os
from pathlib import Path

# App Metadata
APP_NAME = "UUID Generator Pro"
APP_VERSION = "1.0.0"
AUTHOR = "UUID Generator Team"

# Paths
ROOT_DIR = Path(__file__).parent.absolute()
ASSETS_DIR = ROOT_DIR / "assets"
LOGS_DIR = ROOT_DIR / "logs"
HISTORY_DIR = ROOT_DIR / "history"
EXPORTS_DIR = ROOT_DIR / "exports"

# Create necessary directories
for directory in (LOGS_DIR, HISTORY_DIR, EXPORTS_DIR, ASSETS_DIR):
    directory.mkdir(parents=True, exist_ok=True)

SETTINGS_FILE = ROOT_DIR / "settings.json"
HISTORY_FILE = HISTORY_DIR / "history.json"

# UI Defaults
DEFAULT_THEME = "dark"
DEFAULT_COLOR_THEME = "blue"
DEFAULT_WINDOW_SIZE = "900x700"

# Generation defaults
DEFAULT_UUID_VERSION = "4"
DEFAULT_QUANTITY = 10
DEFAULT_NAMESPACE = "DNS"
DEFAULT_NAMESPACE_NAME = "example.com"
MAX_UUIDS = 10_000_000

# Constants for worker threads
CHUNK_SIZE = 50_000

# Namespace mapping for UUID 3 and 5
import uuid
NAMESPACE_MAP = {
    "DNS": uuid.NAMESPACE_DNS,
    "URL": uuid.NAMESPACE_URL,
    "OID": uuid.NAMESPACE_OID,
    "X500": uuid.NAMESPACE_X500
}

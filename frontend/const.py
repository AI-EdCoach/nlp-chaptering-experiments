import os
from pathlib import Path

SCRIPT_PATH = Path(os.path.abspath(__file__))
FRONTEND_DIR = SCRIPT_PATH.parent
STATIC_FRONTEND_DIR = FRONTEND_DIR / "static"
ALLOWED_VIDEO_EXTENSIONS = [".mp4"]

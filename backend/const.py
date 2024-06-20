import os
from pathlib import Path

FILE_PATH = Path(os.path.abspath(__file__))
BACKEND_DIR = FILE_PATH.parent
REPO_DIR = BACKEND_DIR.parent
WORKSPACE_DIR = REPO_DIR.parent

UPLOADED_VIDEOS_ROOT = REPO_DIR / "uploaded_videos"

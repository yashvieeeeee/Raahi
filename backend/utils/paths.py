import os
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
CONFIG_DIR = PROJECT_ROOT / "config"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
RAAHI_ML_DIR = PROJECT_ROOT / "raahi_ml"

if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    INSTANCE_DIR = Path(tempfile.gettempdir()).resolve() / "raahi_instance"
else:
    INSTANCE_DIR = (PROJECT_ROOT / "instance").resolve()

try:
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

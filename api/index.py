import os
import sys
import traceback
from pathlib import Path

# Add project root to sys.path so backend and config are importable
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

init_error = None
flask_app = None

try:
    from backend.main import app as flask_app
except Exception:
    init_error = traceback.format_exc()


def application(environ, start_response):
    if init_error:
        start_response(
            "500 Internal Server Error",
            [("Content-Type", "text/plain; charset=utf-8")],
        )
        return [f"Startup Initialization Error:\n\n{init_error}".encode("utf-8")]

    # If Vercel rewrote the path to /api/index, restore original path if available
    path_info = environ.get("PATH_INFO", "")
    if path_info in {"/api/index", "/api/index/"}:
        raw_uri = environ.get("RAW_URI", "")
        matched_path = environ.get("HTTP_X_MATCHED_PATH", "")
        if raw_uri and not raw_uri.startswith("/api/index"):
            environ["PATH_INFO"] = raw_uri.split("?")[0]
        elif matched_path and not matched_path.startswith("/api/index"):
            environ["PATH_INFO"] = matched_path.split("?")[0]
        else:
            environ["PATH_INFO"] = "/"

    try:
        return flask_app(environ, start_response)
    except Exception:
        runtime_error = traceback.format_exc()
        start_response(
            "500 Internal Server Error",
            [("Content-Type", "text/plain; charset=utf-8")],
        )
        return [f"Runtime Execution Error:\n\n{runtime_error}".encode("utf-8")]


app = application

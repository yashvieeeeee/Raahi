import os
import sys
import traceback
from pathlib import Path
from urllib.parse import parse_qs, urlencode

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

    # Normalize rewritten path from Vercel
    query_string = environ.get("QUERY_STRING", "")
    if "__path" in query_string:
        params = parse_qs(query_string, keep_blank_values=True)
        if "__path" in params:
            raw_path = params.pop("__path", [""])[0]
            environ["PATH_INFO"] = "/" + raw_path.lstrip("/")
            environ["QUERY_STRING"] = urlencode(params, doseq=True)

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

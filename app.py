"""Serve the local V2G demo and connect browser requests to the Python model.

Run with ``python app.py`` and open http://127.0.0.1:8000. This module uses
only Python's standard library. HTML, CSS, and JavaScript come from static/;
calculation logic and validation live in v2g_model.py.

The browser first requests the page and defaults with GET, then sends edited
inputs as JSON with POST /api/calculate. Responses contain results or an error;
requests do not save input changes to disk. The server binds to the local
computer's loopback address and is intended as a local portfolio demo, not a
production hosting service.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

from v2g_model import calculate, load_defaults


ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
HOST = "127.0.0.1"
PORT = 8000


class SimulatorHandler(BaseHTTPRequestHandler):
    """Handle static-file, documentation, and JSON API requests.

    BaseHTTPRequestHandler parses HTTP requests and dispatches them to do_GET
    or do_POST. Those method names are required by the standard-library API.
    ThreadingHTTPServer creates handlers as requests arrive; callers normally
    start the server rather than constructing this class themselves.
    """
    def _send(self, status: int, body: bytes, content_type: str) -> None:
        """Write an HTTP status, response headers, and an already encoded body.

        Args:
            status: HTTP code, such as 200 for success or 400 for invalid input.
            body: Raw response bytes; encode text or JSON before calling.
            content_type: Media type and optional charset identifying the body.

        Content-Length counts bytes, not characters. Cache-Control: no-store
        asks the browser not to retain a cached copy of the response.
        """
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        """Serve defaults, selected documents, or a file beneath static/.

        Routes:
            /api/defaults: Configuration values with source/evidence metadata.
            /SOURCES.md, /PROJECT_SPEC.md, /CODEX_BUILD_PROMPT.md: Plain Markdown.
            /: The demo's index.html page.
            Other paths: Files resolved relative to the static directory.

        Query strings are ignored for routing and URL escapes are decoded.
        Resolved paths outside static/ receive 403; missing files receive 404.
        This containment check prevents a path such as /../app.py from exposing
        project files through the static-file route. The explicitly listed
        documentation files are served separately.
        """
        path = unquote(self.path.split("?", 1)[0])
        if path == "/api/defaults":
            self._send(200, json.dumps(load_defaults()).encode(), "application/json; charset=utf-8")
            return
        if path in {"/SOURCES.md", "/PROJECT_SPEC.md", "/CODEX_BUILD_PROMPT.md"}:
            doc_path = ROOT / path.lstrip("/")
            self._send(200, doc_path.read_bytes(), "text/markdown; charset=utf-8")
            return
        relative = "index.html" if path in ("/", "") else path.lstrip("/")
        file_path = (STATIC / relative).resolve()
        if STATIC.resolve() not in file_path.parents and file_path != STATIC / "index.html":
            self._send(403, b"Forbidden", "text/plain; charset=utf-8")
            return
        if not file_path.is_file():
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return
        content_type = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
        }.get(file_path.suffix, "application/octet-stream")
        self._send(200, file_path.read_bytes(), content_type)

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        """Calculate a scenario from a JSON object sent to /api/calculate.

        Read the declared Content-Length, accepting 0 through 32,000 bytes.
        An empty body means no overrides. Decode the object, reload the defaults,
        and pass both to calculate; the model performs numerical validation.

        Return status 200 and a JSON result on success. Invalid JSON, non-object
        bodies, rejected inputs, and the caught value/type/key errors return
        status 400 with {"error": "message"}. Other POST paths receive 404.
        allow_nan=False prevents non-finite values in successful JSON output.

        This endpoint computes results only; it does not persist edits. Errors
        outside the listed exception types are not translated into this JSON
        error format.
        """
        if self.path != "/api/calculate":
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 <= length <= 32_000:
                raise ValueError("Request is too large.")
            overrides = json.loads(self.rfile.read(length) or b"{}")
            if not isinstance(overrides, dict):
                raise ValueError("Inputs must be provided as a JSON object.")
            result = calculate(load_defaults(), overrides)
            self._send(200, json.dumps(result, allow_nan=False).encode(), "application/json; charset=utf-8")
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
            payload = json.dumps({"error": str(error)}).encode()
            self._send(400, payload, "application/json; charset=utf-8")

    def log_message(self, fmt: str, *args: object) -> None:
        """Print the client address and formatted request log in the terminal.

        The HTTP handler calls this hook for request/status messages. ``*args``
        supplies the values for placeholders in the format string ``fmt``.
        """
        print(f"{self.address_string()} - {fmt % args}")


def main() -> None:
    """Start the local threaded server and close its listening socket on exit.

    Bind to HOST and PORT, print the browser URL, and process requests until
    interrupted with Ctrl+C. The finally block closes the server after the
    serving loop exits, including when an exception interrupts that loop.
    Importing app.py does not start the server: the __main__ guard below calls
    this function only when the file is executed as a script.

    Raises:
        OSError: The server cannot bind, for example because port 8000 is busy.
    """
    server = ThreadingHTTPServer((HOST, PORT), SimulatorHandler)
    print(f"Newark V2G Fleet Value Simulator running at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop the server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping simulator.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

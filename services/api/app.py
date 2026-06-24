import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


REQUEST_COUNT = 0
ERROR_COUNT = 0
LATENCY_BUCKETS = {
    "0.1": 0,
    "0.3": 0,
    "0.5": 0,
    "1.0": 0,
    "+Inf": 0,
}


def reset_metrics() -> None:
    global REQUEST_COUNT, ERROR_COUNT
    REQUEST_COUNT = 0
    ERROR_COUNT = 0
    for bucket in LATENCY_BUCKETS:
        LATENCY_BUCKETS[bucket] = 0


def observe_request(duration_seconds: float, status_code: int) -> None:
    global REQUEST_COUNT, ERROR_COUNT
    REQUEST_COUNT += 1
    if status_code >= 500:
        ERROR_COUNT += 1
    for bucket in LATENCY_BUCKETS:
        if bucket == "+Inf" or duration_seconds <= float(bucket):
            LATENCY_BUCKETS[bucket] += 1


def metrics_text() -> str:
    lines = [
        "# HELP demo_api_requests_total Total API requests.",
        "# TYPE demo_api_requests_total counter",
        f"demo_api_requests_total {REQUEST_COUNT}",
        "# HELP demo_api_errors_total Total API 5xx responses.",
        "# TYPE demo_api_errors_total counter",
        f"demo_api_errors_total {ERROR_COUNT}",
        "# HELP demo_api_request_duration_seconds Request latency histogram.",
        "# TYPE demo_api_request_duration_seconds histogram",
    ]
    cumulative = 0
    for bucket, count in LATENCY_BUCKETS.items():
        cumulative = count
        lines.append(f'demo_api_request_duration_seconds_bucket{{le="{bucket}"}} {cumulative}')
    lines.append(f"demo_api_request_duration_seconds_count {REQUEST_COUNT}")
    return "\n".join(lines) + "\n"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        started = time.monotonic()
        parsed = urlparse(self.path)
        status = 200

        if parsed.path == "/healthz":
            body = {"status": "ok"}
        elif parsed.path == "/readyz":
            if os.getenv("FORCE_NOT_READY", "false").lower() == "true":
                status = 503
                body = {"status": "not_ready"}
            else:
                body = {"status": "ready"}
        elif parsed.path == "/work":
            query = parse_qs(parsed.query)
            delay_ms = int(query.get("delay_ms", ["25"])[0])
            time.sleep(max(delay_ms, 0) / 1000)
            if query.get("fail", ["false"])[0].lower() == "true":
                status = 500
                body = {"status": "error", "message": "simulated failure"}
            else:
                body = {"status": "ok", "delay_ms": delay_ms}
        elif parsed.path == "/metrics":
            self._send_text(200, metrics_text())
            return
        else:
            status = 404
            body = {"status": "not_found"}

        observe_request(time.monotonic() - started, status)
        self._send_json(status, body)

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send_json(self, status: int, body: dict[str, object]) -> None:
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _send_text(self, status: int, body: str) -> None:
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; version=0.0.4")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def run() -> None:
    port = int(os.getenv("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"demo api listening on :{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()

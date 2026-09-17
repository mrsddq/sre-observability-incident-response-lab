import json
import os
import time
from threading import Lock
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


MAX_DELAY_MS = 10_000
METRICS_LOCK = Lock()
REQUEST_COUNT = 0
ERROR_COUNT = 0
LATENCY_SUM = 0.0
LATENCY_BUCKETS = {
    "0.1": 0,
    "0.3": 0,
    "0.5": 0,
    "1.0": 0,
    "+Inf": 0,
}


def reset_metrics() -> None:
    global REQUEST_COUNT, ERROR_COUNT, LATENCY_SUM
    with METRICS_LOCK:
        REQUEST_COUNT = 0
        ERROR_COUNT = 0
        LATENCY_SUM = 0.0
        for bucket in LATENCY_BUCKETS:
            LATENCY_BUCKETS[bucket] = 0


def observe_request(duration_seconds: float, status_code: int) -> None:
    global REQUEST_COUNT, ERROR_COUNT, LATENCY_SUM
    # A scrape must never see a counter updated without its histogram buckets.
    with METRICS_LOCK:
        REQUEST_COUNT += 1
        LATENCY_SUM += duration_seconds
        if status_code >= 500:
            ERROR_COUNT += 1
        for bucket in LATENCY_BUCKETS:
            if bucket == "+Inf" or duration_seconds <= float(bucket):
                LATENCY_BUCKETS[bucket] += 1


def metrics_text() -> str:
    with METRICS_LOCK:
        count, errors, duration_sum = REQUEST_COUNT, ERROR_COUNT, LATENCY_SUM
        buckets = dict(LATENCY_BUCKETS)
    lines = [
        "# HELP demo_api_requests_total Accepted work requests (excludes probes and invalid input).",
        "# TYPE demo_api_requests_total counter",
        f"demo_api_requests_total {count}",
        "# HELP demo_api_errors_total Work requests returning a 5xx response.",
        "# TYPE demo_api_errors_total counter",
        f"demo_api_errors_total {errors}",
        "# HELP demo_api_request_duration_seconds Work processing latency histogram.",
        "# TYPE demo_api_request_duration_seconds histogram",
    ]
    for bucket, bucket_count in buckets.items():
        lines.append(f'demo_api_request_duration_seconds_bucket{{le="{bucket}"}} {bucket_count}')
    lines.append(f"demo_api_request_duration_seconds_count {count}")
    lines.append(f"demo_api_request_duration_seconds_sum {duration_sum}")
    return "\n".join(lines) + "\n"


def parse_delay_ms(query: dict[str, list[str]]) -> int:
    values = query.get("delay_ms", ["25"])
    if len(values) != 1:
        raise ValueError("delay_ms must appear once")
    try:
        delay_ms = int(values[0])
    except ValueError as exc:
        raise ValueError("delay_ms must be an integer") from exc
    if not 0 <= delay_ms <= MAX_DELAY_MS:
        raise ValueError(f"delay_ms must be between 0 and {MAX_DELAY_MS}")
    return delay_ms


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
            query = parse_qs(parsed.query, keep_blank_values=True)
            try:
                delay_ms = parse_delay_ms(query)
            except ValueError as exc:
                self._send_json(400, {"status": "invalid_request", "message": str(exc)})
                return
            time.sleep(delay_ms / 1000)
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

        if parsed.path == "/work":
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

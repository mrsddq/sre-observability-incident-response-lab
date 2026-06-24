import argparse
import sys
import time
import urllib.error
import urllib.request


def check(url: str, timeout: float) -> tuple[bool, float, int | None]:
    started = time.monotonic()
    try:
      with urllib.request.urlopen(url, timeout=timeout) as response:
          elapsed = time.monotonic() - started
          return 200 <= response.status < 400, elapsed, response.status
    except urllib.error.HTTPError as exc:
      elapsed = time.monotonic() - started
      return False, elapsed, exc.code
    except urllib.error.URLError:
      elapsed = time.monotonic() - started
      return False, elapsed, None


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple synthetic HTTP check.")
    parser.add_argument("--url", default="http://localhost:8000/healthz")
    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print("synthetic check configuration is valid")
        return

    ok, elapsed, status = check(args.url, args.timeout)
    print(f"url={args.url} ok={ok} status={status} latency_seconds={elapsed:.3f}")
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

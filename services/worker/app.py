import os
import time


def main() -> None:
    interval = int(os.getenv("WORKER_INTERVAL_SECONDS", "30"))
    while True:
        print("worker heartbeat")
        time.sleep(interval)


if __name__ == "__main__":
    main()

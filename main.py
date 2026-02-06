import argparse
from src.realtime_monitor import monitor_log_file


def main():
    print("Cyber Log Analyzer started successfully")

    parser = argparse.ArgumentParser(description="Cybersecurity Log Analyzer")

    parser.add_argument(
        "--threshold",
        type=int,
        default=3,
        help="Failed attempts before alert"
    )

    parser.add_argument(
        "--realtime",
        action="store_true",
        help="Enable real-time log monitoring"
    )

    args = parser.parse_args()

    if args.realtime:
        monitor_log_file("logs/auth.log", threshold=args.threshold)
        return


if __name__ == "__main__":
    main()

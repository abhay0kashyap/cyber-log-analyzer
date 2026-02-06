import argparse
from src.realtime_monitor import monitor_log_file
from src.parser import get_failed_login_ips
from src.detector import detect_bruteforce


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
    
    # Batch Mode (Default)
    print(f"📂 Analyzing logs/auth.log (Batch Mode)...")
    ips = get_failed_login_ips("logs/auth.log")
    suspicious_ips = detect_bruteforce(ips, threshold=args.threshold)

    if not suspicious_ips:
        print("✅ No suspicious activity detected.")
    else:
        print(f"🚨 Found {len(suspicious_ips)} suspicious IP(s):")
        print("-" * 40)
        for ip, count in suspicious_ips.items():
            print(f"❌ IP: {ip:<15} | Failed Attempts: {count}")
        print("-" * 40)

if __name__ == "__main__":
    main()

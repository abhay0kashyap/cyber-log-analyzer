import argparse
import csv
from src.parser import get_failed_login_ips
from src.detector import detect_bruteforce

print("Cyber Log Analyzer started successfully")

# Argument parser
parser = argparse.ArgumentParser(description="Cybersecurity Log Analyzer")
parser.add_argument(
    "--threshold",
    type=int,
    default=2,
    help="Number of failed attempts before marking IP as suspicious"
)

args = parser.parse_args()

# Detection logic
ips = get_failed_login_ips()
attackers = detect_bruteforce(ips, threshold=args.threshold)

print(f"\n🚨 Brute-Force Attackers Detected (threshold = {args.threshold}):")

if not attackers:
    print("No suspicious activity detected.")
else:
    for ip, attempts in attackers.items():
        print(f"{ip} → {attempts} failed attempts")

    # STEP: Save report to CSV
    report_file = "reports/attack_report.csv"
    with open(report_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ip_address", "failed_attempts"])

        for ip, attempts in attackers.items():
            writer.writerow([ip, attempts])

    print(f"\n📁 Report saved to {report_file}")

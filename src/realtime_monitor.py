import time
import re
from collections import Counter
from src.alert import send_email_alert

IP_PATTERN = r"\b\d{1,3}(?:\.\d{1,3}){3}\b"


def monitor_log_file(log_path, threshold=3):
    print(f"📡 Monitoring {log_path} in real-time (threshold={threshold})...\n")

    failed_ip_counter = Counter()
    alerted_ips = set()  # 🔒 remembers alerted IPs

    with open(log_path, "r") as file:
        file.seek(0, 2)  # move to end of file

        while True:
            line = file.readline()

            if not line:
                time.sleep(1)
                continue

            if "Failed password" not in line:
                continue

            match = re.search(IP_PATTERN, line)
            if not match:
                continue

            ip = match.group()
            failed_ip_counter[ip] += 1

            print(f"❌ Failed login from {ip} (count={failed_ip_counter[ip]})")

            # 🚨 ALERT ONLY ONCE
            if failed_ip_counter[ip] == threshold:
                if ip not in alerted_ips:
                    print(f"\n🚨 ALERT: Brute-force attack detected from {ip}!\n")
                    send_email_alert(ip, failed_ip_counter[ip])
                    alerted_ips.add(ip)

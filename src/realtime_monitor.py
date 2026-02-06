import time
import re
from collections import Counter

from src.geoip import get_ip_details
from src.alert import send_email_alert

# Regex pattern to extract IPv4 addresses
IP_PATTERN = r"\b\d{1,3}(?:\.\d{1,3}){3}\b"


def monitor_log_file(log_path, threshold=3):
    print(f"📡 Monitoring {log_path} in real-time (threshold={threshold})...\n")

    failed_ip_counter = Counter()
    alerted_ips = set()  # to avoid repeated alerts for same IP

    with open(log_path, "r") as file:
        # Move cursor to end of file (like tail -f)
        file.seek(0, 2)

        while True:
            line = file.readline()

            if not line:
                time.sleep(1)
                continue

            # Only process failed login attempts
            if "Failed password" not in line:
                continue

            match = re.search(IP_PATTERN, line)
            if not match:
                continue

            ip = match.group()
            failed_ip_counter[ip] += 1

            print(f"❌ Failed login from {ip} (count={failed_ip_counter[ip]})")

            # Trigger alert exactly once per IP
            if failed_ip_counter[ip] >= threshold and ip not in alerted_ips:
                print("\n🚨 ALERT: Brute-force attack detected!")
                print(f"🔢 Failed Attempts: {failed_ip_counter[ip]}")
                print(f"🌐 Attacker IP: {ip}")

                # --- GEO-IP ENRICHMENT ---
                geo = get_ip_details(ip)
                if geo:
                    print("\n📍 Attacker Intelligence:")
                    print(f"🌍 Country: {geo.get('country')}")
                    print(f"🏙 City: {geo.get('city')}")
                    print(f"🏢 ISP: {geo.get('isp')}")
                    print(f"🛰 ASN: {geo.get('asn')}")
                    print(f"☁ Hosting Provider: {geo.get('hosting')}")
                    print(f"🕵 Proxy/VPN: {geo.get('proxy')}")

                # --- EMAIL ALERT ---
                send_email_alert(
                    ip=ip,
                    attempts=failed_ip_counter[ip],
                    enrich=geo,
                    classification="Brute-Force Login Attempt",
                    threshold=threshold
                )

                alerted_ips.add(ip)
                print("✅ Alert processed successfully\n")

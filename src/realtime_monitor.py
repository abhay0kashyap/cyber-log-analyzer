import time
import re
from collections import Counter

from src.geoip import get_ip_details
from src.alert import send_email_alert
from src.csv_logger import log_attack_to_csv

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
                print(f"⚠️  Ignored line (No IPv4 found): {line.strip()}")
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
                print("\n📍 Attacker Intelligence:")
                if geo:
                    print(f"🌍 Country: {geo.get('country')}")
                    print(f"🏙 City (ISP Node): {geo.get('city')}")
                    print(f"📍 Approx Coordinates: {geo.get('lat')}, {geo.get('lon')}")
                    print(f"🗺 Google Maps: {geo.get('map_url')}")
                    print(f"🏢 ISP: {geo.get('isp')}")
                    print(f"🛰 ASN: {geo.get('asn')}")
                    print(f"☁ Hosting Provider: {'Yes' if geo.get('hosting') else 'No'}")
                    print(f"🕵 Proxy/VPN: {'Yes' if geo.get('proxy') else 'No'}")
                    print("   (Note: Location is based on ISP gateway, not exact GPS)")
                else:
                    print("⚠️  Location data unavailable.")
                    print("   (This usually happens for Local IPs like 192.168.x.x or 127.0.0.1)")

                # --- EMAIL ALERT ---
                send_email_alert(
                    ip=ip,
                    attempts=failed_ip_counter[ip],
                    enrich=geo,
                    classification="Brute-Force Login Attempt",
                    threshold=threshold
                )

                # --- CSV LOGGING ---
                log_attack_to_csv(ip, failed_ip_counter[ip], geo)

                alerted_ips.add(ip)
                print("✅ Alert processed successfully\n")

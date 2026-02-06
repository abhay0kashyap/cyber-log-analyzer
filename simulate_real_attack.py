import time
import requests
import os
import random

LOG_FILE = "logs/auth.log"

def get_public_ip():
    """Fetches the external public IP of this machine."""
    try:
        print("🌍 Fetching your public IP address...")
        # Uses a public API to get your real IP (seen by the internet)
        return requests.get("https://api.ipify.org", timeout=5).text
    except Exception as e:
        print(f"❌ Failed to get public IP: {e}")
        return "127.0.0.1"

def simulate():
    print("Select Simulation Mode:")
    print("1. Attack from MY IP (Tests your ISP location)")
    print("2. Attack from RANDOM Global IP (Tests map/country detection)")
    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "2":
        # Random IPs from US, China, Russia, Brazil to show variety
        fake_ips = ["128.101.101.101", "202.108.22.5", "77.88.55.77", "200.147.67.142"]
        public_ip = random.choice(fake_ips)
        print(f"🌍 Selected Random Global IP: {public_ip}")
    else:
        public_ip = get_public_ip()
        print(f"🌍 Selected Your IP: {public_ip}")

    print(f"🎯 Simulating brute-force attack...")
    
    # Ensure logs directory exists
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    with open(LOG_FILE, "a") as f:
        # Write enough entries to trigger the threshold (default 3)
        for i in range(1, 4):
            timestamp = time.strftime("%b %d %H:%M:%S")
            # Format matches standard Linux auth.log
            log_entry = f"{timestamp} server sshd[12345]: Failed password for invalid user admin from {public_ip} port {50000+i} ssh2\n"
            
            f.write(log_entry)
            f.flush()
            print(f"💥 [{i}/3] Logged failed attempt from {public_ip}")
            time.sleep(1)

if __name__ == "__main__":
    simulate()
import csv
import os
from datetime import datetime

CSV_FILE = "logs/attacks.csv"

def log_attack_to_csv(ip, attempts, enrich=None):
    """
    Appends attack details to a CSV file for historical analysis.
    """
    # Ensure logs directory exists
    os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)
    
    file_exists = os.path.isfile(CSV_FILE)
    
    headers = [
        "Timestamp", "IP", "Attempts", "Country", "City", 
        "ISP", "ASN", "Latitude", "Longitude", "Map URL", "Hosting", "Proxy"
    ]
    
    # Handle missing enrichment data safely
    if not enrich:
        enrich = {}

    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ip,
        attempts,
        enrich.get("country", "Unknown"),
        enrich.get("city", "Unknown"),
        enrich.get("isp", "Unknown"),
        enrich.get("asn", "Unknown"),
        enrich.get("lat", ""),
        enrich.get("lon", ""),
        enrich.get("map_url", ""),
        "Yes" if enrich.get("hosting") else "No",
        "Yes" if enrich.get("proxy") else "No"
    ]

    try:
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(headers)
            writer.writerow(row)
        print(f"📝 Attack logged to {CSV_FILE}")
    except Exception as e:
        print(f"❌ Failed to log to CSV: {e}")
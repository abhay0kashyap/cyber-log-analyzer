from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import re

app = FastAPI()

# ✅ Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------
# ROOT
# ---------------------------------------------------
@app.get("/")
def root():
    return {"message": "Cyber Log Analyzer API running 🚀"}


# ---------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}


# ---------------------------------------------------
# STATS ENDPOINT (Dynamic)
# ---------------------------------------------------
@app.get("/stats")
def get_stats():

    total_events = 0
    windows_events = 0
    syslog_events = 0
    unique_devices = set()

    # Adjust path if needed
    log_path = "../logs/auth.log"

    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8", errors="ignore") as file:
            lines = file.readlines()
            total_events = len(lines)

            for line in lines:

                # Example Windows detection
                if "Windows" in line:
                    windows_events += 1

                # Example Syslog detection
                if "syslog" in line.lower():
                    syslog_events += 1

                # Extract IP addresses
                ips = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", line)
                for ip in ips:
                    unique_devices.add(ip)

    return {
        "total_events": total_events,
        "windows_events": windows_events,
        "syslog_events": syslog_events,
        "all_devices": len(unique_devices),
    }

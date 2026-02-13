from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# -----------------------------
# CORS Configuration
# -----------------------------
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Root Endpoint
# -----------------------------
@app.get("/")
def root():
    return {"message": "Cyber Log Analyzer API running 🚀"}


# -----------------------------
# Health Check
# -----------------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}


# -----------------------------
# Stats Endpoint (For Dashboard)
# -----------------------------
@app.get("/stats")
def get_stats():
    return {
        "total_events": 7333000,
        "windows_events": 6407000,
        "syslog_events": 269000,
        "all_devices": 44,
    }


# -----------------------------
# Alerts Endpoint (Optional)
# -----------------------------
@app.get("/alerts")
def get_alerts():
    return [
        {"id": 1, "type": "Brute Force", "severity": "High"},
        {"id": 2, "type": "Malware Detection", "severity": "Critical"},
        {"id": 3, "type": "Suspicious Login", "severity": "Medium"},
    ]

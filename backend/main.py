from fastapi import FastAPI
from realtime_monitor import monitor_log_file

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Cyber Log Analyzer API running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
@app.get("/stats")
def get_stats():
    return {
        "total_events": 7333000,
        "windows_events": 6407000,
        "syslog_events": 269000,
        "all_devices": 44
    }

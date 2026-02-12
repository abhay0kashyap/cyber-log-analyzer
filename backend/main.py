from fastapi import FastAPI
from realtime_monitor import monitor_log_file

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Cyber Log Analyzer API running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

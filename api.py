from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
import os
import csv
from typing import Dict

# Import your existing log analysis functions
from src.parser import get_failed_login_ips
from src.detector import detect_bruteforce

# Define the path for uploaded logs and reports
UPLOAD_DIR = "uploaded_logs"
REPORT_PATH = "reports/attack_report.csv"

# Create the upload directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)

app = FastAPI()

def create_attack_report(attacks: Dict[str, int], report_path: str):
    """
    Creates a CSV report of detected attacks.
    """
    headers = ["IP", "Attempts"]
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for ip, attempts in attacks.items():
            writer.writerow([ip, attempts])

@app.get("/")
def read_root():
    return {"message": "Cyber Log Analyzer API is running."}

@app.post("/analyze/")
async def analyze_logs(file: UploadFile = File(...)):
    """
    Analyzes an uploaded log file for security attacks.
    """
    log_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # Save the uploaded log file
    with open(log_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        # Process the log file
        failed_ips = get_failed_login_ips(log_path)
        suspicious_ips = detect_bruteforce(failed_ips)
        
        # Create a CSV report
        if suspicious_ips:
            create_attack_report(suspicious_ips, REPORT_PATH)
            return JSONResponse(
                status_code=200,
                content={
                    "message": f"Analysis complete. Found {len(suspicious_ips)} potential attacks.",
                    "report_path": REPORT_PATH,
                    "attacks": suspicious_ips
                }
            )
        else:
            return JSONResponse(
                status_code=200,
                content={"message": "Analysis complete. No potential attacks found."}
            )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"An error occurred during analysis: {str(e)}"}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
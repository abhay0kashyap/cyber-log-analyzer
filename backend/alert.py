alerts = []

def create_alert(data):
    alert = {
        "type": "Brute Force",
        "message": f"Multiple failed logins from {data.get('ip')}",
        "severity": "High"
    }
    alerts.append(alert)
    print("ALERT:", alert)

def get_alerts():
    return alerts

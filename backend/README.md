# Backend API Documentation

## Quick Start

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Health & Status

**GET /api/health**
- Returns health status of the API
- Response:
```json
{
  "status": "healthy",
  "service": "cyber-log-analyzer",
  "timestamp": "2024-01-01T00:00:00",
  "monitoring_active": false
}
```

### Monitor Control

**POST /api/monitor/start?threshold=3**
- Starts real-time log monitoring
- Parameters:
  - `threshold` (int): Failed attempts before alert (1-20, default: 3)
- Response:
```json
{
  "status": "success",
  "message": "Real-time monitoring started (threshold: 3)",
  "is_running": true
}
```

**POST /api/monitor/stop**
- Stops real-time monitoring
- Response:
```json
{
  "status": "success",
  "message": "Real-time monitoring stopped",
  "is_running": false
}
```

**GET /api/monitor/status**
- Returns current monitoring status
- Response:
```json
{
  "is_running": true
}
```

### Events API

**GET /api/events**
- Returns all security events
- Query Parameters:
  - `event_type` (str): Filter by event type
  - `ip` (str): Filter by IP address
  - `limit` (int): Max results (1-1000, default: 100)
  - `offset` (int): Skip results (default: 0)
- Response:
```json
[
  {
    "id": 1,
    "timestamp": "2024-01-01T00:00:00",
    "event_type": "failed_login",
    "ip_address": "192.168.1.1",
    "country": "United States",
    "city": "New York",
    "isp": "Comcast",
    "asn": "AS7922",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "is_proxy": false,
    "is_hosting": false
  }
]
```

**GET /api/events/stats**
- Returns event statistics
- Response:
```json
{
  "total_events": 150,
  "events_today": 25,
  "top_attacking_ips": [
    {"ip": "192.168.1.1", "count": 50},
    {"ip": "10.0.0.1", "count": 30}
  ]
}
```

### Alerts API

**GET /api/alerts**
- Returns alerts
- Query Parameters:
  - `active_only` (bool): Show only active alerts (default: true)
  - `severity` (str): Filter by severity
- Response:
```json
[
  {
    "id": 1,
    "timestamp": "2024-01-01T00:00:00",
    "alert_type": "bruteforce",
    "severity": "high",
    "source_ip": "192.168.1.1",
    "description": "Brute-force attack detected: 15 failed login attempts",
    "is_active": true,
    "acknowledged": false
  }
]
```

**POST /api/alerts/{alert_id}/acknowledge**
- Acknowledges an alert
- Response:
```json
{
  "message": "Alert acknowledged"
}
```

### Intelligence API

**GET /api/intelligence**
- Returns attacker intelligence
- Query Parameters:
  - `limit` (int): Max results (1-500, default: 50)
- Response:
```json
[
  {
    "id": 1,
    "ip_address": "192.168.1.1",
    "first_seen": "2024-01-01T00:00:00",
    "last_seen": "2024-01-01T12:00:00",
    "total_attempts": 15,
    "country": "United States",
    "city": "New York",
    "isp": "Comcast",
    "asn": "AS7922",
    "is_proxy": false,
    "is_hosting": false,
    "threat_level": "high"
  }
]
```

**GET /api/intelligence/{ip}**
- Returns details for a specific IP
- Response:
```json
{
  "ip": "192.168.1.1",
  "cached": true,
  "country": "United States",
  "city": "New York",
  "isp": "Comcast",
  "asn": "AS7922",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "is_proxy": false,
  "is_hosting": false,
  "map_url": "https://www.google.com/maps?q=40.7128,-74.0060"
}
```

### Dashboard Stats API

**GET /api/stats**
- Returns comprehensive dashboard statistics
- Response:
```json
{
  "total_events": 150,
  "total_attacks": 10,
  "unique_ips": 5,
  "active_alerts": 3,
  "events_today": 25,
  "attacks_today": 2,
  "top_countries": [
    {"country": "United States", "count": 50},
    {"country": "China", "count": 30}
  ],
  "recent_activity": [
    {
      "timestamp": "2024-01-01T12:00:00",
      "type": "failed_login",
      "ip": "192.168.1.1",
      "country": "United States"
    }
  ]
}
```

### Analysis API

**POST /api/analyze?threshold=3**
- Analyzes the auth.log file for attacks
- Response:
```json
{
  "message": "Analysis started in background",
  "threshold": 3
}
```

### Reports API

**GET /api/reports/export**
- Exports attack report as CSV
- Returns: CSV file download

## Database Schema

### Tables

#### security_events
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| timestamp | DateTime | Event timestamp |
| event_type | String | Type of event |
| ip_address | String | Source IP |
| country | String | Country (optional) |
| city | String | City (optional) |
| isp | String | ISP name (optional) |
| asn | String | ASN (optional) |
| latitude | Float | Latitude (optional) |
| longitude | Float | Longitude (optional) |
| map_url | String | Google Maps URL (optional) |
| is_proxy | Boolean | Is proxy/VPN |
| is_hosting | Boolean | Is hosting/cloud |
| raw_log | Text | Raw log line |

#### alerts
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| timestamp | DateTime | Alert timestamp |
| alert_type | String | Alert type |
| severity | String | Severity level |
| source_ip | String | Source IP |
| description | String | Alert description |
| is_active | Boolean | Is active |
| acknowledged | Boolean | Is acknowledged |

#### attacker_intelligence
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| ip_address | String | IP address (unique) |
| first_seen | DateTime | First seen |
| last_seen | DateTime | Last seen |
| total_attempts | Integer | Total attempts |
| country | String | Country |
| city | String | City |
| isp | String | ISP |
| asn | String | ASN |
| is_proxy | Boolean | Is proxy |
| is_hosting | Boolean | Is hosting |
| latitude | Float | Latitude |
| longitude | Float | Longitude |
| threat_level | String | Threat level |

## Environment Variables

Create a `.env` file:

```env
SENDER_EMAIL=your_email@gmail.com
APP_PASSWORD=your_app_password
RECEIVER_EMAIL=admin@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

## Running with Docker

```dockerfile
FROM python:3.9
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```


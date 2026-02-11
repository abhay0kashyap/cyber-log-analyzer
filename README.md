# Cyber Log Analyzer - SIEM System

A professional Security Information and Event Management (SIEM) system designed for real-time detection, analysis, and visualization of SSH brute-force attacks. It features a robust FastAPI backend for data processing and a modern React dashboard for intuitive monitoring.

## 🛡️ Features

### Backend (FastAPI)
- **Real-time Log Monitoring**: Continuously monitors auth.log for failed login attempts
- **Attack Detection**: Identifies brute-force attacks based on configurable thresholds
- **Geo-IP Enrichment**: Automatically enriches attack data with location, ISP, ASN, proxy/VPN detection
- **Persistent Storage**: Uses SQLite to store security events, alerts, and comprehensive attacker intelligence
- **RESTful API**: Full API for frontend integration with real-time data access
- **Email Alerts**: Configurable email notifications for detected attacks
- **Report Export**: Allows exporting attacker intelligence data to CSV for further analysis

### Frontend (React Dashboard)
- **SIEM-style Dashboard**: Professional dark-themed security dashboard
- **Real-time Stats**: Live counters for events, attacks, unique IPs, and active alerts
- **Interactive Charts**: Visualize attack trends and top attacking countries
- **Events Log**: Complete security events history with filtering
- **Alerts Management**: View, acknowledge, and manage security alerts
- **Attacker Intelligence**: Detailed IP information including geo-location, ISP, proxy status
- **Real-time Updates**: 5-second auto-refresh for a dynamic, real-time monitoring experience
- **Responsive Design**: Works on desktop and mobile devices

## 📂 Project Structure

```
cyber-log-analyzer/
├── backend/
│   ├── app/
│   │   └── main.py           # FastAPI backend application
│   ├── requirements.txt       # Backend dependencies
│   └── README.md            # Backend documentation
│
├── webapp/
│   ├── public/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx # Main dashboard component
│   │   │   └── index.ts      # Page exports
│   │   ├── services/
│   │   │   └── api.ts        # API service layer
│   │   ├── App.tsx           # Main React app
│   │   ├── index.tsx         # Entry point
│   │   └── index.css         # Global styles
│   ├── package.json          # Frontend dependencies
│   └── README.md            # Frontend documentation
│
├── src/                      # Core Python modules
│   ├── parser.py            # Log parsing utilities
│   ├── detector.py          # Attack detection logic
│   ├── geoip.py             # IP geolocation
│   ├── alert.py             # Email notifications
│   ├── csv_logger.py        # CSV logging
│   └── realtime_monitor.py  # Real-time monitoring
│
├── logs/
│   ├── auth.log             # Log file to monitor
│   └── attacks.csv          # Attack history
│
├── reports/                 # Generated reports
├── uploaded_logs/           # Uploaded log files
├── main.py                  # CLI entry point
├── api.py                   # (Legacy) Original API - not actively used in current setup
├── index.html               # Simple client-side HTML frontend for Flask API
├── app.py                   # Simple Flask API for basic dashboard (alternative to full SIEM)
└── README.md                # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+ and npm
- Git

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/cyber-log-analyzer.git
cd cyber-log-analyzer
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Install core dependencies
pip install requests python-dotenv
```

### 3. Frontend Setup

```bash
cd webapp

# Install dependencies
npm install

# Create environment file
echo "REACT_APP_API_URL=http://localhost:8000" > .env
```

### 4. Configure Email Alerts (Optional)

Create a `.env` file in the project root:

```env
SENDER_EMAIL=your_email@gmail.com
APP_PASSWORD=your_google_app_password
RECEIVER_EMAIL=admin@example.com
```

> **Note**: For Gmail, use an App Password instead of your regular password.

## 🖥️ Running the Application

### Terminal 1: Start the Backend

```bash
# From project root
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs

### Terminal 2: Start the Frontend

```bash
cd webapp
npm start
```

The dashboard will open at: http://localhost:3000

## 📡 API Endpoints

### Health & Status
- `GET /api/health` - Health check
- `GET /api/monitor/status` - Monitor status

### Monitor Control
- `POST /api/monitor/start?threshold=3` - Start real-time monitoring
- `POST /api/monitor/stop` - Stop monitoring
- `POST /api/analyze?threshold=3` - Analyze log file

### Events
- `GET /api/events` - Get all events with filters
- `GET /api/events/stats` - Event statistics

### Alerts
- `GET /api/alerts` - Get alerts (active_only=true by default)
- `POST /api/alerts/{id}/acknowledge` - Acknowledge alert

### Intelligence
- `GET /api/intelligence` - Get attacker intelligence
- `GET /api/intelligence/{ip}` - Get IP details

### Dashboard
- `GET /api/stats` - Dashboard statistics

### Reports
- `GET /api/reports/export` - Export attack report (CSV)

## 🎮 Usage

### 1. Real-Time Monitoring

1. Open the dashboard at http://localhost:3000
2. Click "Start Monitor" to begin real-time monitoring
3. Set the threshold (default: 3 failed attempts)
4. Watch for attacks as they happen!

### 2. Batch Analysis

Click "Analyze Logs" to analyze the existing auth.log file without real-time monitoring.

### 3. View Events & Alerts

- Navigate to the **Events** tab to see all security events
- Navigate to the **Alerts** tab to see active alerts
- Click "Acknowledge" when you've reviewed an alert

### 4. Attacker Intelligence

Navigate to the **Intelligence** tab to see:
- Total attack attempts per IP
- Geo-location information
- ISP/ASN details
- Proxy/VPN detection
- Hosting provider identification

## 🧪 Testing

### Simulate Attacks

Use the simulation script to test the system:

```bash
# Terminal 1: Start monitoring
python main.py --realtime --threshold 3

# Terminal 2: Run simulation
python simulate_real_attack.py
```

## 🔧 Configuration

### Threshold Settings

The threshold determines how many failed login attempts trigger an alert:
- **Low (1-2)**: Very sensitive, many alerts
- **Medium (3-5)**: Balanced (recommended)
- **High (10+)**: Only severe attacks

### Email Notifications

Configure email alerts in `.env`:
```env
SENDER_EMAIL=alerts@example.com
APP_PASSWORD=your_app_password
RECEIVER_EMAIL=admin@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

## 🛡️ Security Features

1. **Brute-Force Detection**: Detects repeated failed login attempts
2. **Geo-IP Enrichment**: Identifies attack origins worldwide
3. **Proxy/VPN Detection**: Flags anonymized connections
4. **Hosting Detection**: Identifies attacks from cloud providers
5. **Email Alerts**: Instant notifications for critical attacks
6. **Threat Level Assessment**: Categorizes attackers by risk level

## 📊 Database Schema

### Tables
- **security_events**: Individual failed login attempts
- **alerts**: Active security alerts
- **attacker_intelligence**: Aggregated attacker data

### Event Types
- `failed_login`: Individual failed login attempt
- `attack_detected`: Confirmed attack pattern

### Alert Severities
- `low`: Minor suspicious activity
- `medium`: Standard attack detected
- `high`: Significant attack
- `critical`: Severe attack requiring immediate attention

## 🐳 Docker (Optional)

```dockerfile
# Backend
FROM python:3.9
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with FastAPI and React
- IP Geolocation provided by IP-API.com
- Inspired by modern SIEM solutions

---

**🛡️ Cyber Log Analyzer - Protect Your Systems**

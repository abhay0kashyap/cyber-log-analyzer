# 🛡️ Cyber Log Analyzer

Hi there! Welcome to **Cyber Log Analyzer**.

This is a custom-built security tool designed to protect Linux servers from **Brute-Force SSH Attacks**. If you've ever wondered who is trying to guess your server passwords or where those attacks are coming from, this tool is for you.

It works by monitoring your system logs in real-time. When it detects someone trying to break in (by failing to login multiple times), it doesn't just alert you—it investigates them. It pulls their location, ISP, and even checks if they are using a VPN or Proxy, then sends all that intel directly to your email.

---

## ✨ What Can It Do?

Here is why this tool is useful:

- **👀 Watch Logs Live**: It tails your `auth.log` file continuously, so it catches attacks the moment they happen.
- **🚨 Smart Detection**: It counts failed login attempts. If an IP fails too many times (you choose the limit), it triggers an alarm.
- **🌍 Geo-Location Tracking**: It instantly finds out where the attacker is located (Country, City, Coordinates) and generates a **Google Maps link** for you.
- **🕵️ VPN & Proxy Detection**: It checks if the attacker is hiding behind a proxy or cloud hosting provider.
- **📧 Instant Email Alerts**: You get a detailed report in your inbox immediately.
- **📝 History Logging**: Every attack is saved to a CSV file (`logs/attacks.csv`) so you can analyze trends later.
- **🧪 Safe Simulation**: Includes a built-in simulator so you can test the alerts without needing a real hacker to attack you.

---

## 🛠️ How to Set It Up

Follow these steps to get it running on your machine.

### 1. Get the Code
First, clone this repository to your local machine:
```bash
git clone https://github.com/yourusername/cyber-log-analyzer.git
cd cyber-log-analyzer
```

### 2. Install Dependencies
Ensure you have Python 3 installed. Then install the required packages:
```bash
pip install requests python-dotenv
```

### 3. Configure Environment Variables
Create a `.env` file in the project root to store your email credentials securely:

```ini
# .env
SENDER_EMAIL=your_email@gmail.com
APP_PASSWORD=your_google_app_password
RECEIVER_EMAIL=admin_email@example.com
```
> **Note:** If using Gmail, you must generate an App Password instead of using your regular login password.

### 4. Prepare Log Directory
Ensure the logs directory exists (or point the tool to your system's `/var/log/auth.log`):
```bash
mkdir -p logs
touch logs/auth.log
```

---

## 🖥️ Usage

### 📡 Real-Time Monitoring (Recommended)
Start the monitor to watch for new attacks live:
```bash
python main.py --realtime --threshold 3
```
- **`--threshold`**: Number of failed attempts before triggering an alert (default: 3).

### 📂 Batch Analysis
Analyze the existing log file for past attacks without monitoring:
```bash
python main.py --threshold 5
```

---

## 🧪 Testing & Simulation

You can safely test the system without waiting for a real attack.

1. **Start the Monitor** in one terminal:
   ```bash
   python main.py --realtime
   ```

2. **Run the Simulation Script** in a second terminal:
   ```bash
   python simulate_real_attack.py
   ```
   
   **Options:**
   - **Mode 1 (My IP):** Fetches your public IP and logs failed attempts. Useful for testing ISP location accuracy.
   - **Mode 2 (Random Global IP):** Uses random IPs (e.g., from Russia, China, US) to test map links and country detection.

---

## 📂 Project Structure

```
cyber-log-analyzer/
├── main.py                  # Entry point for the application
├── simulate_real_attack.py  # Script to generate fake attack logs
├── .env                     # Configuration file (not committed)
├── logs/
│   ├── auth.log             # Target log file
│   └── attacks.csv          # History of detected attacks
└── src/
    ├── alert.py             # Email notification logic
    ├── csv_logger.py        # CSV logging logic
    ├── detector.py          # Batch detection logic
    ├── geoip.py             # IP geolocation API integration
    ├── parser.py            # Log parsing utilities
    └── realtime_monitor.py  # Real-time monitoring engine
```

## ⚠️ Disclaimer
This tool is intended for **educational and defensive purposes only**. Ensure you have permission to monitor the logs and network traffic on the system where this is installed.
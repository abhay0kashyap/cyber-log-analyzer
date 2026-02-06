import smtplib
from email.message import EmailMessage

SENDER_EMAIL = "cattack482@gmail.com"
APP_PASSWORD = "hfmlvxrdjlfvirrr"  # app password WITHOUT spaces
RECEIVER_EMAIL = "cattack482@gmail.com"


def send_email_alert(ip, attempts):
    msg = EmailMessage()
    msg["Subject"] = "🚨 Brute-Force Attack Detected"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    msg.set_content(
        f"""
ALERT 🚨

Brute-force attack detected!

IP Address: {ip}
Failed Attempts: {attempts}

Please check your server immediately.
"""
    )

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)

        print("📧 Email alert sent successfully!")

    except Exception as e:
        print("❌ Email sending failed:", e)

from src.parser import get_failed_login_ips

print("Cyber Log Analyzer started successfully")

ips = get_failed_login_ips()

print("\n🚨 Failed Login IP Addresses:")
for ip in ips:
    print(ip)

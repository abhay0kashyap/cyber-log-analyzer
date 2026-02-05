import re

def get_failed_login_ips():
    file = open("logs/auth.log", "r")

    failed_ips = []

    # REGEX pattern to find IP addresses
    ip_pattern = r"\b\d{1,3}(?:\.\d{1,3}){3}\b"

    for line in file:
        if "Failed password" in line:
            match = re.search(ip_pattern, line)
            if match:
                failed_ips.append(match.group())

    file.close()
    return failed_ips

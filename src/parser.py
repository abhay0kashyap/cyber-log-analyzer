import re

def get_failed_login_ips(log_path="logs/auth.log"):
    failed_ips = []

    # REGEX pattern to find IP addresses
    ip_pattern = r"\b\d{1,3}(?:\.\d{1,3}){3}\b"

    with open(log_path, "r") as file:
        for line in file:
            if "Failed password" in line:
                match = re.search(ip_pattern, line)
                if match:
                    failed_ips.append(match.group())

    return failed_ips

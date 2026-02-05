from collections import Counter

def detect_bruteforce(ips, threshold=2):
    """
    Detect IPs with failed login attempts >= threshold
    """
    ip_counts = Counter(ips)

    suspicious_ips = {}

    for ip, count in ip_counts.items():
        if count >= threshold:
            suspicious_ips[ip] = count

    return suspicious_ips

import requests

def get_ip_details(ip):
    """
    Fetch geolocation details for an IP address
    """
    try:
        url = f"http://ip-api.com/json/{ip}"
        response = requests.get(url, timeout=5)
        data = response.json()

        if data["status"] != "success":
            return None

        return {
            "ip": ip,
            "country": data.get("country", "Unknown"),
            "region": data.get("regionName", "Unknown"),
            "city": data.get("city", "Unknown"),
            "isp": data.get("isp", "Unknown"),
            "org": data.get("org", "Unknown"),
            "asn": data.get("as", "Unknown"),
            "hosting": data.get("hosting", False),
            "proxy": data.get("proxy", False)
        }

    except Exception as e:
        print("❌ GeoIP lookup failed:", e)
        return None

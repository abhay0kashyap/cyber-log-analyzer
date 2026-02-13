from __future__ import annotations


def mock_geo_from_ip(ip: str) -> dict:
    try:
        first = int(ip.split(".")[0])
    except Exception:
        return {"country": "Unknown", "city": "Unknown", "lat": 0.0, "lng": 0.0}

    if first < 50:
        return {"country": "US", "city": "New York", "lat": 40.7128, "lng": -74.0060}
    if first < 100:
        return {"country": "DE", "city": "Frankfurt", "lat": 50.1109, "lng": 8.6821}
    if first < 150:
        return {"country": "SG", "city": "Singapore", "lat": 1.3521, "lng": 103.8198}
    if first < 200:
        return {"country": "BR", "city": "Sao Paulo", "lat": -23.5505, "lng": -46.6333}
    return {"country": "AU", "city": "Sydney", "lat": -33.8688, "lng": 151.2093}

import requests


def geocode_address(address: str, city: str, postcode: str, country: str):
    full_query = f"{address}, {postcode}, {city}, {country}"

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": full_query,
        "format": "json",
        "limit": 1,
    }

    headers = {
        "User-Agent": "QRWaver/1.0 (contact: support@qrwaver.com)"
    }

    r = requests.get(url, params=params, headers=headers, timeout=5)

    if not r.ok:
        return None, None

    data = r.json()

    if not data:
        return None, None

    return data[0]["lat"], data[0]["lon"]

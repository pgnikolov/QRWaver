def build_location_payload(data: dict) -> str:
    """
    Builds the payload for a Location QR code.

    Expected input:
    {
        "type": "location",
        "data": {
            "lat": 42.6977,
            "lng": 23.3219
        }
    }

    Returns:
        str: A geo: URI usable in map apps.
    """
    location = data.get("data", {})
    lat = location.get("lat", 0)
    lng = location.get("lng", 0)

    return f"geo:{lat},{lng}"

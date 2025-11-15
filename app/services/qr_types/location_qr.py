def build_location_payload(data: dict) -> str:
    lat = data.get("lat")
    lng = data.get("lng")

    if not lat or not lng:
        return ""

    # Universal link format (works on iPhone + Android)
    return f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"

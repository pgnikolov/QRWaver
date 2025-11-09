def build_menu_payload(data) -> str:
    """
    Builds the payload for a restaurant/menu QR code.

    Expected input:
    {
        "type": "menu",
        "data": "https://myrestaurant.com/menu"
    }

    Returns:
        str: A valid URL (ensured https://).
    """
    if isinstance(data, dict):
        url = data.get("data", "")
    else:
        url = data

    url = str(url).strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url

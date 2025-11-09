def build_url_payload(data: dict) -> str:
    """
    Builds the payload for a URL QR code.

    Expected input:
    {
        "type": "url",
        "data": "https://example.com"
    }

    Returns:
        str: The URL string to encode.
    """
    url = data.get("data", "").strip()

    # Ensure the URL has a valid scheme
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url

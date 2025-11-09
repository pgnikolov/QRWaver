def build_youtube_payload(data) -> str:
    """
    Builds the payload for a YouTube QR code.

    Expected input:
    {
        "type": "youtube",
        "data": "https://youtube.com/watch?v=abc123"
    }

    Returns:
        str: The video URL (ensured https://).
    """
    if isinstance(data, dict):
        url = data.get("data", "")
    else:
        url = data

    url = str(url).strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url

def build_appstore_payload(data: dict) -> str:
    """
    Builds payload for an app store link.

    Example:
        {
            "type": "appstore",
            "data": {"platform": "ios", "url": "https://apps.apple.com/app/id123456"}
        }
    """
    app = data.get("data", {})
    url = app.get("url", "").strip()

    return url or "https://appstore.com"

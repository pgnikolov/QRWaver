def build_social_payload(data: dict) -> str:
    """
    Builds payload for a social profile QR.

    Example:
        {"type": "social", "data": {"platform": "instagram", "username": "qrweaver"}}
    """
    d = data.get("data", {})
    platform = d.get("platform", "").lower()
    username = d.get("username", "").lstrip("@")

    base_urls = {
        "instagram": f"https://instagram.com/{username}",
        "facebook": f"https://facebook.com/{username}",
        "twitter": f"https://twitter.com/{username}",
        "tiktok": f"https://tiktok.com/@{username}",
        "linkedin": f"https://linkedin.com/in/{username}",
        "youtube": f"https://youtube.com/@{username}",
    }

    return base_urls.get(platform, f"https://{platform}.com/{username}")

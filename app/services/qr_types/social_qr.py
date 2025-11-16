def build_social_payload(data: dict) -> str:
    """
    Build direct URLs for social network QR codes.
    Works with both username and full URLs.
    """

    network = data.get("network", "").lower().strip()
    username = data.get("username", "").strip()

    if not network or not username:
        return ""

    # If full URL, return as is
    if username.startswith("http://") or username.startswith("https://"):
        return username

    # Otherwise, build from username
    base_urls = {
        "facebook": f"https://www.facebook.com/{username}",
        "instagram": f"https://www.instagram.com/{username}",
        "linkedin": f"https://www.linkedin.com/in/{username}",
        "twitter": f"https://www.twitter.com/{username}",
        "tiktok": f"https://www.tiktok.com/@{username}",
        "youtube": f"https://www.youtube.com/@{username}",
    }

    return base_urls.get(network, "")

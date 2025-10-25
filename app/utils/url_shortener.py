import re


def create_social_shortlink(profile_url, platform):
    """Create shortlinks for social media profiles"""

    # Clean the profile URL
    profile_url = profile_url.strip()

    if platform == "facebook":
        if "facebook.com" in profile_url:
            if "/profile.php" in profile_url:
                match = re.search(r'id=(\d+)', profile_url)
                if match:
                    return f"fb.com/{match.group(1)}"
                return "fb.com/profile"
            else:
                username = profile_url.split("facebook.com/")[-1].split("/")[0].split("?")[0]
                return f"fb.com/{username}" if username else "fb.com"
        return f"fb.com/{profile_url.replace('@', '').replace('/', '')}"

    elif platform == "instagram":
        if "instagram.com" in profile_url:
            username = profile_url.split("instagram.com/")[-1].split("/")[0].split("?")[0]
            return f"instagram.com/{username}" if username else "instagram.com"
        return f"instagram.com/{profile_url.replace('@', '').replace('/', '')}"

    elif platform == "linkedin":
        if "linkedin.com" in profile_url:
            username = profile_url.split("linkedin.com/in/")[-1].split("/")[0].split("?")[0]
            return f"linkedin.com/in/{username}" if username else "linkedin.com"
        return f"linkedin.com/in/{profile_url.replace('@', '').replace('/', '')}"

    return profile_url


def get_full_url(shortlink, platform):
    """Convert shortlink to full URL"""
    if not shortlink.startswith(('http://', 'https://')):
        return f"https://{shortlink}"
    return shortlink

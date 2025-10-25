import re


def create_social_shortlink(profile_url, platform):
    """
    Generates a shortened or formatted social media URL based on the given profile URL and
    specified platform. Cleans and parses the input URL and adjusts it for Facebook, Instagram,
    or LinkedIn platforms. If the provided profile URL is already clean, it ensures proper
    platform-specific formatting.

    :param profile_url: The profile URL to be shortened or formatted.
    :type profile_url: str
    :param platform: The name of the social media platform. Acceptable values are 'facebook',
        'instagram', or 'linkedin'.
    :type platform: str
    :return: The formatted or shortened social media URL. If no matching platform rules are met,
        the given profile URL remains unaltered.
    :rtype: str
    """

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
    """
    Generates the full URL for a given shortlink, ensuring it includes the proper
    protocol (https://) if missing. Useful for standardizing short URLs across
    different platforms.

    :param shortlink: A string representing the short URL that may or may not
        include the protocol (http:// or https://).
    :type shortlink: str
    :param platform: An identifier for the platform where the shortlink is used.
        This parameter determines platform-specific URL handling logic.
    :type platform: str
    :return: A string containing the full URL with the appropriate protocol.
    :rtype: str
    """
    if not shortlink.startswith(('http://', 'https://')):
        return f"https://{shortlink}"
    return shortlink

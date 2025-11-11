def build_url_payload(data):
    """
    Builds a complete URL payload by validating and formatting the given data.

    This function ensures that the provided data, either in dictionary or raw string
    format, is converted into a valid, formatted URL. It trims any extraneous spaces
    and automatically prepends "https://" if the scheme is missing.

    :param data: Input data containing the URL or its components. Can be a dictionary
                 with a key `url` holding the URL string or a raw string representing
                 the URL.
    :type data: Union[dict, str]
    :raises ValueError: If the URL is empty or invalid.
    :return: A fully formatted, valid URL.
    :rtype: str
    """
    # Accept dict or raw string
    if isinstance(data, dict):
        url = (data.get("url") or "").strip()
    else:
        url = str(data or "").strip()

    if not url:
        raise ValueError("URL cannot be empty")

    # Auto-add https:// if missing
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url

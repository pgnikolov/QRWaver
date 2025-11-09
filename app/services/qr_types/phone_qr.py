def build_phone_payload(data) -> str:
    """
    Builds the payload for a phone QR code.

    Expected input:
    {
        "type": "phone",
        "data": "+359888123456"
    }

    Returns:
        str: The phone number formatted as tel:+359888123456
    """
    if isinstance(data, dict):
        number = data.get("data", "")
    else:
        number = data

    return f"tel:{str(number).strip()}"

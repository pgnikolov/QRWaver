def build_text_payload(data) -> str:
    """
    Builds the payload for a plain text QR code.

    Expected input: a string or {"data": "..."}.
    Returns the text itself.
    """
    if isinstance(data, dict):
        text = data.get("data", "")
    else:
        text = data

    return str(text).strip()

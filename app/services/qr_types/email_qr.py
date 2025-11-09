from urllib.parse import quote


def build_email_payload(data: dict) -> str:
    """
    Builds the payload for an Email QR code.

    Expected input:
    {
        "type": "email",
        "data": {
            "to": "example@email.com",
            "subject": "Hello",
            "body": "This is a test email."
        }
    }

    Returns:
        str: A properly formatted mailto: URI.
    """
    email_data = data.get("data", {})
    to = email_data.get("to", "")
    subject = quote(email_data.get("subject", ""))
    body = quote(email_data.get("body", ""))

    return f"mailto:{to}?subject={subject}&body={body}"

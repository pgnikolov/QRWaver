from urllib.parse import quote

def build_email_payload(data):
    email = data.get("to", "")
    subject = data.get("subject", "")
    body = data.get("body", "")

    if not email:
        return "mailto:"

    payload = f"mailto:{email}"

    params = []
    if subject:
        params.append(f"subject={quote(subject)}")
    if body:
        params.append(f"body={quote(body)}")

    if params:
        payload += "?" + "&".join(params)

    return payload

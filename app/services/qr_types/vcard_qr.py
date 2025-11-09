def build_vcard_payload(data: dict) -> str:
    """
    Builds payload for a vCard (contact info) QR.

    Example:
        {
            "type": "vcard",
            "data": {
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+123456789",
                "email": "john@doe.com",
                "company": "QRWeaver",
                "title": "Developer"
            }
        }
    """
    v = data.get("data", {})
    return (
        "BEGIN:VCARD\n"
        "VERSION:3.0\n"
        f"N:{v.get('last_name','')};{v.get('first_name','')}\n"
        f"FN:{v.get('first_name','')} {v.get('last_name','')}\n"
        f"ORG:{v.get('company','')}\n"
        f"TITLE:{v.get('title','')}\n"
        f"TEL:{v.get('phone','')}\n"
        f"EMAIL:{v.get('email','')}\n"
        "END:VCARD"
    )

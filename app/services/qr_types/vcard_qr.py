def build_vcard_payload(data: dict) -> str:
    v = data

    first = v.get("first_name", "")
    last = v.get("last_name", "")

    phone = v.get("phone", "")
    mobile = v.get("mobile", "")
    fax = v.get("fax", "")
    email = v.get("email", "")
    website = v.get("url", "").strip()

    company = v.get("company", "")
    title = v.get("title", "")

    address = v.get("address", "")
    city = v.get("city", "")
    postcode = v.get("postcode", "")
    country = v.get("country", "")

    crlf = "\r\n"

    adr = f";;{address};{city};;{postcode};{country}"

    payload = (
            "BEGIN:VCARD" + crlf +
            "VERSION:3.0" + crlf +
            f"N:{last};{first};;;" + crlf +
            f"FN:{first} {last}".strip() + crlf
    )

    if company:
        payload += f"ORG:{company}" + crlf
    if title:
        payload += f"TITLE:{title}" + crlf
    if phone:
        payload += f"TEL;TYPE=work,voice:{phone}" + crlf
    if mobile:
        payload += f"TEL;TYPE=cell,voice:{mobile}" + crlf
    if fax:
        payload += f"TEL;TYPE=fax:{fax}" + crlf
    if email:
        payload += f"EMAIL;TYPE=internet:{email}" + crlf
    if website and website != "https://":
        payload += f"URL:{website}" + crlf

    if any([address, city, postcode, country]):
        # Standard ADR
        payload += f"ADR;TYPE=WORK:{adr}" + crlf

        # Apple Maps Thumbnail Support
        payload += (
                f"item1.ADR;TYPE=WORK:{adr}" + crlf +
                "item1.X-ABLabel:Work" + crlf
        )

    payload += "END:VCARD"

    return payload

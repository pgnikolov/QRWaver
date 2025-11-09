def build_wifi_payload(data: dict) -> str:
    """
    Builds the payload for a Wi-Fi QR code.

    Expected input:
    {
        "type": "wifi",
        "data": {
            "ssid": "MyWiFi",
            "password": "12345678",
            "encryption": "WPA2",   # WPA, WPA2, WEP, or nopass
            "hidden": false
        }
    }

    Returns:
        str: The formatted Wi-Fi connection string (WIFI:T:...).
    """
    wifi_data = data.get("data", {})
    ssid = wifi_data.get("ssid", "")
    password = wifi_data.get("password", "")
    encryption = wifi_data.get("encryption", "WPA").upper()
    hidden = wifi_data.get("hidden", False)

    return f"WIFI:T:{encryption};S:{ssid};P:{password};H:{'true' if hidden else 'false'};;"

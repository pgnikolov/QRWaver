def build_wifi_payload(data: dict) -> str:
    """
    Builds a correct Wi-Fi QR payload.
    """

    wifi = data.get("data", {}) if "data" in data else data

    ssid = wifi.get("ssid", "").replace(";", "\\;")
    password = wifi.get("password", "").replace(";", "\\;")
    enc = (wifi.get("encryption") or "").upper()
    hidden = wifi.get("hidden", False)

    # ✅ Normalize encryption values
    if enc in ["WPA/WPA2", "WPA2", "WPA3", "WPA WPA2"]:
        enc = "WPA"

    if enc in ["NONE", "NO PASSWORD", "NOPASS", ""]:
        enc = "nopass"

    if enc not in ["WPA", "WEP", "nopass"]:
        enc = "WPA"

    # ✅ Build QR payload using official spec
    return f"WIFI:T:{enc};S:{ssid};P:{password};H:{'true' if hidden else 'false'};;"

def build_crypto_payload(data: dict) -> str:
    """
    Builds payload for a crypto payment QR.

    Example:
        {
            "type": "crypto",
            "data": {
                "currency": "BTC",
                "address": "1BitcoinAddress123",
                "amount": "0.01"
            }
        }
    """
    c = data.get("data", {})
    currency = c.get("currency", "BTC")
    address = c.get("address", "YOUR_ADDRESS_HERE")
    amount = c.get("amount", "0.01")
    return f"{currency}:{address}?amount={amount}"

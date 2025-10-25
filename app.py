from app import create_app

app = create_app()

if __name__ == '__main__':
    print("🚀 Стартиране на QRWeaver...")
    print("📍 Достъпен на: http://127.0.0.1:5000")
    print("📘 Facebook QR: http://127.0.0.1:5000/social/facebook")
    print("📷 Instagram QR: http://127.0.0.1:5000/social/instagram")
    print("💼 LinkedIn QR: http://127.0.0.1:5000/social/linkedin")

    app.run(debug=True, host='127.0.0.1', port=5000)

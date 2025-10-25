class QRService:
    """Business logic layer for QR operations"""

    def __init__(self):
        self.supported_platforms = ['facebook', 'instagram', 'linkedin']

    def validate_social_input(self, platform, profile_url, display_name):
        """Валидира входните данни за социални QR кодове"""
        errors = []

        if platform not in self.supported_platforms:
            errors.append(f"Неподдържана платформа: {platform}")

        if not profile_url or not profile_url.strip():
            errors.append("URL на профила е задължителен")

        if not display_name or not display_name.strip():
            errors.append("Име за показване е задължително")

        if len(display_name) > 50:
            errors.append("Името трябва да е под 50 символа")

        return errors

    def generate_filename(self, platform, display_name):
        """Генерира име на файл за QR кода"""
        clean_name = ''.join(c for c in display_name if c.isalnum() or c in (' ', '-', '_')).strip()
        clean_name = clean_name.replace(' ', '_')
        return f"qr_{platform}_{clean_name}.png"

class QRService:
    """
    Handles QR code service functionalities, including validation of inputs specific
    to social platforms and generation of filenames for QR codes.

    The class is intended to support QR code generation for various social media
    platforms. This includes validating input details and formatting a proper file
    name for storing the generated QR code.

    :ivar supported_platforms: List of platforms supported by the QR code service.
    :type supported_platforms: list
    """

    def __init__(self):
        self.supported_platforms = ['facebook', 'instagram', 'linkedin']

    def validate_social_input(self, platform, profile_url, display_name):
        """
        Validates the social media input parameters including the platform,
        profile URL, and display name. The method checks whether the platform
        is supported, if the profile URL is provided, and if the display
        name meets required conditions such as being non-empty and
        within the character limit.

        :param platform: The name of the social media platform
        :type platform: str
        :param profile_url: The URL of the user's profile
        :type profile_url: str
        :param display_name: The display name of the user
        :type display_name: str
        :return: A list of validation error messages if any issues are found
        :rtype: list[str]
        """
        errors = []

        if platform not in self.supported_platforms:
            errors.append(f"Unsupported platform: {platform}")

        if not profile_url or not profile_url.strip():
            errors.append("Profile URL is required")

        if not display_name or not display_name.strip():
            errors.append("Display name is required.")

        if len(display_name) > 50:
            errors.append("Name must be under 50 characters.")

        return errors

    def generate_filename(self, platform, display_name):
        """
        Generates a filename for a QR code image by formatting the platform and display
        name into a standardized naming convention. This function ensures the filename
        contains only alphanumeric characters, underscores, and dashes, replacing
        spaces with underscores for compatibility.

        :param platform: The platform name to be included in the filename.
        :type platform: str
        :param display_name: The display name that identifies the content of the QR code.
        :type display_name: str
        :return: A formatted filename for the QR code image.
        :rtype: str
        """
        clean_name = ''.join(c for c in display_name if c.isalnum() or c in (' ', '-', '_')).strip()
        clean_name = clean_name.replace(' ', '_')
        return f"qr_{platform}_{clean_name}.png"

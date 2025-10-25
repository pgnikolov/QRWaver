import qrcode
from PIL import Image, ImageDraw, ImageFont
from .style_utils import add_rounded_corners
from .url_shortener import create_social_shortlink, get_full_url


class SocialQRGenerator:
    """Универсален генератор за социални мрежи"""

    # Платформени цветове в RGB формат
    PLATFORM_COLORS = {
        "facebook": (63, 92, 153),  # Facebook blue
        "instagram": [
            (64, 93, 230),  # Instagram blue
            (88, 81, 219),  # Instagram purple-blue
            (131, 58, 180),  # Instagram purple
            (193, 53, 132),  # Instagram magenta
            (225, 48, 108)  # Instagram pink
        ],
        "linkedin": (34, 89, 130),  # LinkedIn blue
        "twitter": (29, 161, 242),  # Twitter blue
        "youtube": (255, 0, 0)  # YouTube red
    }

    def __init__(self):
        self.logo_paths = {
            "facebook": "static/images/logos/facebook_logo.png",
            "instagram": "static/images/logos/instagram_logo.png",
            "linkedin": "static/images/logos/linkedin_logo.png"
        }

    def generate_social_qr(self, platform, profile_url, display_name,
                           use_shortlink=True, rounded_corners=False,
                           corner_radius=40, qr_size=300):
        """Генерира QR код за социална мрежа с опции"""

        try:
            # Създаване на shortlink
            if use_shortlink:
                shortlink = create_social_shortlink(profile_url, platform)
                qr_data = get_full_url(shortlink, platform)
            else:
                shortlink = profile_url
                qr_data = get_full_url(profile_url, platform)

            # Генериране на QR код
            qr_image = self._create_base_qr(qr_data, platform, qr_size)

            # Добавяне на лого
            qr_image = self._add_logo(qr_image, platform, qr_size)

            # Добавяне на текст
            final_image = self._add_text_section(qr_image, platform, display_name, shortlink, qr_size)

            # Прилагане на rounded corners ако е избрано
            if rounded_corners:
                final_image = add_rounded_corners(final_image, corner_radius)

            return final_image, shortlink, qr_data

        except Exception as e:
            raise Exception(f"Грешка при генериране на QR код: {str(e)}")

    def _create_base_qr(self, data, platform, size):
        """Създава базов QR код с платформен цвят"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # Вземане на цветове за платформата
        colors = self.PLATFORM_COLORS.get(platform, [(0, 0, 0)])  # Черно по подразбиране

        if platform == "instagram" and len(colors) > 1:
            return self._create_gradient_qr(qr, colors, size)
        else:
            # Вземи първия цвят (за платформи с един цвят)
            main_color = colors[0] if isinstance(colors[0], tuple) else colors
            return self._create_solid_qr(qr, main_color, size)

    def _create_solid_qr(self, qr, color, size):
        """Създава QR код с един цвят"""
        # Увери се, че цветът е в правилен формат
        if isinstance(color, tuple):
            fill_color = color
        else:
            fill_color = (0, 0, 0)  # Черно по подразбиране

        qr_img = qr.make_image(fill_color=fill_color, back_color="white")
        return qr_img.resize((size, size))

    def _create_gradient_qr(self, qr, colors, size):
        """Създава QR код с градиент (за Instagram)"""
        qr_modules = qr.get_matrix()
        box_size = 10
        border = 4
        width = len(qr_modules) * box_size + 2 * border * box_size

        qr_img = Image.new('RGB', (width, width), 'white')
        draw = ImageDraw.Draw(qr_img)

        # Рисуване на QR с градиент
        for y, row in enumerate(qr_modules):
            for x, module in enumerate(row):
                if module:
                    color_index = (x + y) % len(colors)
                    color = colors[color_index]

                    x_pos = x * box_size + border * box_size
                    y_pos = y * box_size + border * box_size
                    draw.rectangle(
                        [x_pos, y_pos, x_pos + box_size, y_pos + box_size],
                        fill=color
                    )

        return qr_img.resize((size, size))

    def _add_logo(self, qr_image, platform, qr_size):
        """Добавя лого в центъра на QR кода"""
        try:
            logo_path = self.logo_paths.get(platform)
            logo_img = Image.open(logo_path).convert('RGBA')
        except:
            # Fallback лого
            logo_img = self._create_fallback_logo(platform)

        # Resize лого
        logo_size = qr_size // 5
        logo_img = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

        # Бял фон за логото
        logo_bg_size = logo_size + 20
        logo_bg = Image.new('RGB', (logo_bg_size, logo_bg_size), 'white')
        logo_pos = ((logo_bg_size - logo_size) // 2, (logo_bg_size - logo_size) // 2)

        if logo_img.mode == 'RGBA':
            logo_bg.paste(logo_img, logo_pos, logo_img)
        else:
            logo_bg.paste(logo_img, logo_pos)

        # Поставяне на лого върху QR кода
        qr_pos = ((qr_size - logo_bg_size) // 2, (qr_size - logo_bg_size) // 2)
        qr_image.paste(logo_bg, qr_pos)

        return qr_image

    def _add_text_section(self, qr_image, platform, display_name, shortlink, qr_size):
        """Добавя текстова секция под QR кода"""
        text_height = 120
        total_height = qr_size + text_height

        final_img = Image.new('RGB', (qr_size, total_height), 'white')
        final_img.paste(qr_image, (0, 0))

        draw = ImageDraw.Draw(final_img)

        # Зареждане на шрифтове
        try:
            font_large = ImageFont.truetype("arialbd.ttf", 24)
            font_medium = ImageFont.truetype("arial.ttf", 16)
            font_small = ImageFont.truetype("arial.ttf", 14)
        except:
            font_large = font_medium = font_small = ImageFont.load_default()

        # Вземи цвета на платформата
        platform_color = self.PLATFORM_COLORS.get(platform, [(0, 0, 0)])[0]

        # Display name
        name_width = draw.textlength(display_name, font=font_large)
        name_x = (qr_size - name_width) // 2
        draw.text((name_x, qr_size + 15), display_name, fill=platform_color, font=font_large)

        # Shortlink
        shortlink_width = draw.textlength(shortlink, font=font_medium)
        shortlink_x = (qr_size - shortlink_width) // 2
        draw.text((shortlink_x, qr_size + 50), shortlink, fill=(51, 51, 51), font=font_medium)  # Dark gray

        # Scan text
        scan_text = self._get_scan_text(platform)
        scan_width = draw.textlength(scan_text, font=font_small)
        scan_x = (qr_size - scan_width) // 2
        draw.text((scan_x, qr_size + 80), scan_text, fill=(102, 102, 102), font=font_small)  # Gray

        # Platform color bar
        bar_height = 6
        bar_y = total_height - bar_height
        draw.rectangle([0, bar_y, qr_size, bar_y + bar_height], fill=platform_color)

        return final_img

    def _get_scan_text(self, platform):
        """Връща подходящ текст за сканиране според платформата"""
        texts = {
            "facebook": "Scan to follow on Facebook",
            "instagram": "Scan to follow on Instagram",
            "linkedin": "Scan to connect on LinkedIn",
            "twitter": "Scan to follow on Twitter",
            "youtube": "Scan to subscribe on YouTube"
        }
        return texts.get(platform, "Scan QR code")

    def _create_fallback_logo(self, platform):
        """Създава fallback лого ако няма файл"""
        size = 80
        logo = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(logo)
        color = self.PLATFORM_COLORS.get(platform, [(0, 0, 0)])[0]

        if platform == "facebook":
            draw.rectangle([20, 10, 60, 70], fill=color)
            draw.rectangle([25, 15, 55, 35], fill='white')
            draw.polygon([(35, 35), (45, 35), (45, 65), (35, 65)], fill='white')
        elif platform == "instagram":
            draw.ellipse([10, 10, 70, 70], outline=color, width=8)
            draw.ellipse([30, 30, 50, 50], fill=color)
        elif platform == "linkedin":
            draw.rectangle([0, 0, 80, 80], fill=color)
            draw.text((20, 15), "in", fill='white')

        return logo


# Удобни функции за бърз достъп
def generate_facebook_qr(profile_url, display_name, **kwargs):
    generator = SocialQRGenerator()
    return generator.generate_social_qr("facebook", profile_url, display_name, **kwargs)


def generate_instagram_qr(profile_url, display_name, **kwargs):
    generator = SocialQRGenerator()
    return generator.generate_social_qr("instagram", profile_url, display_name, **kwargs)


def generate_linkedin_qr(profile_url, display_name, **kwargs):
    generator = SocialQRGenerator()
    return generator.generate_social_qr("linkedin", profile_url, display_name, **kwargs)
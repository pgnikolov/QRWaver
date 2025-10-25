from PIL import Image, ImageDraw


def add_rounded_corners(image, radius=40):
    """Add rounded corners to any image"""
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # Create a mask with rounded corners
    mask = Image.new('L', image.size, 0)
    mask_draw = ImageDraw.Draw(mask)

    # Draw rounded rectangle on mask
    mask_draw.rounded_rectangle([(0, 0), image.size], radius=radius, fill=255)

    # Create result image with transparency
    result = Image.new('RGBA', image.size, (0, 0, 0, 0))
    result.paste(image, (0, 0), mask)

    return result


def apply_modern_frame(image, frame_color="#f8f9fa", padding=20, corner_radius=30):
    """Add modern frame with padding around QR code"""
    # Calculate new size with padding
    new_width = image.width + 2 * padding
    new_height = image.height + 2 * padding

    # Create new image with background
    framed = Image.new('RGB', (new_width, new_height), frame_color)

    # Paste original image centered
    framed.paste(image, (padding, padding))

    # Apply rounded corners to the entire frame
    return add_rounded_corners(framed, corner_radius)

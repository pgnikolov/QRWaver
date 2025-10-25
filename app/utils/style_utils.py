from PIL import Image, ImageDraw


def add_rounded_corners(image, radius=40):
    """
    Adds rounded corners to an input image by creating a mask with the specified
    corner radius and applying it to the image. The function ensures the output
    image retains transparency.

    :param image: The input image to which rounded corners should be applied.
    :type image: PIL.Image.Image
    :param radius: The radius of the rounded corners. Default is 40.
    :type radius: int
    :return: A new image with the same size as the input image, but with rounded
        corners and RGBA transparency.
    :rtype: PIL.Image.Image
    """
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
    """
    Apply a modern styled frame with padding, color, and rounded corners to an image.

    This function adds a styled frame around the input image by increasing its
    dimensions according to the specified padding value. The frame's color and
    corner radius can also be adjusted to suit the desired aesthetic.

    :param image: The input image to which the frame should be applied. Must be an
        instance of the Image class.
    :param frame_color: The color of the frame. Defaults to "#f8f9fa".
    :param padding: The padding added around the input image within the frame.
        Defaults to 20.
    :param corner_radius: The radius for the rounded corners of the frame.
        Defaults to 30.
    :return: A new instance of the Image class with the frame applied.
    :rtype: Image
    """
    # Calculate new size with padding
    new_width = image.width + 2 * padding
    new_height = image.height + 2 * padding

    # Create new image with background
    framed = Image.new('RGB', (new_width, new_height), frame_color)

    # Paste original image centered
    framed.paste(image, (padding, padding))

    # Apply rounded corners to the entire frame
    return add_rounded_corners(framed, corner_radius)

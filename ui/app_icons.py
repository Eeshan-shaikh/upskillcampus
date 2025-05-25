from customtkinter import CTkImage
import base64
import io
from PIL import Image, ImageTk

def get_lock_icon(size=32, color=None):
    """
    Get a lock icon as a CTkImage.
    
    Args:
        size: Size of the icon
        color: Color of the icon (None for default)
        
    Returns:
        CTkImage: Lock icon image
    """
    # SVG data for a lock icon
    svg_data = """
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-lock">
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
        <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
    </svg>
    """
    
    # Replace color if specified
    if color:
        svg_data = svg_data.replace('stroke="currentColor"', f'stroke="{color}"')
    
    # Create a PNG from SVG
    try:
        from cairosvg import svg2png
        png_data = svg2png(bytestring=svg_data.encode('utf-8'), output_width=size, output_height=size)
        img = Image.open(io.BytesIO(png_data))
    except ImportError:
        # Fallback if cairosvg is not available
        img = create_fallback_lock_icon(size)
    
    return CTkImage(light_image=img, dark_image=img, size=(size, size))

def create_fallback_lock_icon(size=32):
    """
    Create a simple lock icon as a fallback.
    
    Args:
        size: Size of the icon
        
    Returns:
        PIL.Image: Lock icon image
    """
    # Create a blank image
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    
    # We'll draw a simple lock shape using PIL
    from PIL import ImageDraw
    
    draw = ImageDraw.Draw(img)
    
    # Calculate dimensions
    padding = size // 6
    body_width = size - 2 * padding
    body_height = size * 3 // 5
    body_top = size * 2 // 5
    
    # Draw the lock body (rectangle with rounded corners)
    draw.rectangle(
        (padding, body_top, padding + body_width, body_top + body_height),
        outline=(100, 100, 100, 255),
        width=max(1, size // 16)
    )
    
    # Draw the lock shackle (U shape)
    shackle_width = body_width * 2 // 3
    shackle_left = padding + (body_width - shackle_width) // 2
    shackle_right = shackle_left + shackle_width
    shackle_top = padding
    shackle_bottom = body_top
    
    # Draw the U shape as three lines
    line_width = max(1, size // 16)
    draw.line(
        (shackle_left, shackle_bottom, shackle_left, shackle_top),
        fill=(100, 100, 100, 255),
        width=line_width
    )
    draw.line(
        (shackle_left, shackle_top, shackle_right, shackle_top),
        fill=(100, 100, 100, 255),
        width=line_width
    )
    draw.line(
        (shackle_right, shackle_top, shackle_right, shackle_bottom),
        fill=(100, 100, 100, 255),
        width=line_width
    )
    
    return img

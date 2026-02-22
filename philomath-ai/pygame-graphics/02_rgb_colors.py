"""
RGB Color Model - Understanding Digital Colors
===============================================

Every color on a computer screen is made of three components:
- R: Red   (0-255)
- G: Green (0-255)
- B: Blue  (0-255)

By mixing these three primary colors of light, you can create any visible color.
This is called the additive color model (unlike painting where mixing creates darker colors).

Learning Objectives:
- Understand how RGB colors work
- Create common colors using RGB values
- Mix colors to create new ones
- Distinguish between light colors (255) and dark colors (0)
- Understand color intensity and gradients

Key Color Facts:
- (0, 0, 0)       = Black (no light)
- (255, 255, 255)  = White (all light)
- (255, 0, 0)      = Pure Red
- (0, 255, 0)      = Pure Green
- (0, 0, 255)      = Pure Blue
- (255, 255, 0)    = Yellow (red + green)
- (0, 255, 255)    = Cyan (green + blue)
- (255, 0, 255)    = Magenta (red + blue)
- (128, 128, 128)  = Gray (equal medium amounts)
- (255, 165, 0)    = Orange
- (139, 69, 19)    = Brown (dark orange-red)
"""

# Primary colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Secondary colors (mixing two primaries)
YELLOW = (255, 255, 0)    # Red + Green
CYAN = (0, 255, 255)      # Green + Blue
MAGENTA = (255, 0, 255)   # Red + Blue

# Useful colors for drawing
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
LIGHT_BLUE = (135, 206, 235)
DARK_GREEN = (0, 100, 0)
PINK = (255, 182, 193)
PURPLE = (128, 0, 128)

# Snow colors (for the snowperson!)
SNOW_WHITE = (240, 240, 255)     # Slightly blue-white (like real snow)
YELLOW_SNOW = (255, 255, 100)    # The snow is yellow! (classic joke from the video)
CARROT_ORANGE = (255, 140, 0)    # For the carrot nose
COAL_BLACK = (20, 20, 20)        # Coal eyes and buttons
SCARF_RED = (200, 0, 0)          # Red scarf
HAT_BLACK = (10, 10, 10)         # Black hat

# Sky and background colors
SKY_BLUE = (135, 206, 250)
NIGHT_BLUE = (25, 25, 112)
SUNSET_ORANGE = (255, 140, 0)

# Game of Life colors
CELL_ALIVE = (50, 200, 50)       # Green for living cells
CELL_DEAD = (30, 30, 30)         # Dark gray for dead cells
BACKGROUND = (15, 15, 15)        # Near-black background
GRID_LINE = (50, 50, 50)         # Subtle grid lines


def mix_colors(color1, color2, ratio=0.5):
    """
    Mix two RGB colors together.

    Args:
        color1: First color as (R, G, B) tuple
        color2: Second color as (R, G, B) tuple
        ratio: How much of color1 to use (0.0 = all color2, 1.0 = all color1)

    Returns:
        Mixed color as (R, G, B) tuple with integer values 0-255
    """
    r = int(color1[0] * ratio + color2[0] * (1 - ratio))
    g = int(color1[1] * ratio + color2[1] * (1 - ratio))
    b = int(color1[2] * ratio + color2[2] * (1 - ratio))
    return (r, g, b)


def darken_color(color, factor=0.5):
    """
    Darken a color by reducing its RGB values.

    Args:
        color: Color as (R, G, B) tuple
        factor: How much to darken (0.0 = black, 1.0 = original)

    Returns:
        Darkened color as (R, G, B) tuple
    """
    return (
        int(color[0] * factor),
        int(color[1] * factor),
        int(color[2] * factor)
    )


def lighten_color(color, factor=0.5):
    """
    Lighten a color by blending it with white.

    Args:
        color: Color as (R, G, B) tuple
        factor: How much of the original to keep (0.0 = white, 1.0 = original)

    Returns:
        Lightened color as (R, G, B) tuple
    """
    return mix_colors(color, WHITE, factor)


def invert_color(color):
    """
    Invert a color (subtract each component from 255).

    Args:
        color: Color as (R, G, B) tuple

    Returns:
        Inverted color as (R, G, B) tuple
    """
    return (255 - color[0], 255 - color[1], 255 - color[2])


def color_brightness(color):
    """
    Calculate the perceived brightness of a color.

    Uses standard luminance weights:
    Y = 0.299*R + 0.587*G + 0.114*B

    Args:
        color: Color as (R, G, B) tuple

    Returns:
        Brightness value from 0 (darkest) to 255 (brightest)
    """
    return 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]


def is_light_color(color):
    """
    Determine if a color is light or dark.

    Useful for deciding whether to use black or white text on a background.

    Args:
        color: Color as (R, G, B) tuple

    Returns:
        True if the color is light (brightness > 128), False if dark
    """
    return color_brightness(color) > 128


def create_gradient(color1, color2, steps):
    """
    Create a gradient between two colors.

    Args:
        color1: Starting color as (R, G, B) tuple
        color2: Ending color as (R, G, B) tuple
        steps: Number of colors in the gradient

    Returns:
        List of (R, G, B) tuples from color1 to color2
    """
    if steps <= 1:
        return [color1]

    gradient = []
    for i in range(steps):
        ratio = 1.0 - (i / (steps - 1))
        gradient.append(mix_colors(color1, color2, ratio))
    return gradient


def describe_color(color):
    """
    Get a text description of a color's components.

    Args:
        color: Color as (R, G, B) tuple

    Returns:
        String description of the color
    """
    r, g, b = color
    desc = f"R={r}, G={g}, B={b}"

    if r > 200 and g > 200 and b > 200:
        name = "near-white"
    elif r < 50 and g < 50 and b < 50:
        name = "near-black"
    elif r > g and r > b:
        name = "reddish"
    elif g > r and g > b:
        name = "greenish"
    elif b > r and b > g:
        name = "bluish"
    elif r > 200 and g > 200:
        name = "yellowish"
    elif g > 200 and b > 200:
        name = "cyanish"
    elif r > 200 and b > 200:
        name = "magentaish"
    else:
        name = "grayish"

    return f"{desc} ({name})"


def main():
    """
    Main demonstration of RGB color model.
    """
    print("=" * 60)
    print("RGB COLOR MODEL")
    print("=" * 60)

    print("\nPrimary Colors:")
    for name, color in [("Black", BLACK), ("White", WHITE),
                         ("Red", RED), ("Green", GREEN), ("Blue", BLUE)]:
        print(f"  {name:10}: {describe_color(color)}")

    print("\nSecondary Colors (mixing two primaries):")
    for name, color in [("Yellow", YELLOW), ("Cyan", CYAN), ("Magenta", MAGENTA)]:
        print(f"  {name:10}: {describe_color(color)}")

    print("\nSnowperson Colors:")
    for name, color in [("Snow White", SNOW_WHITE), ("Yellow Snow", YELLOW_SNOW),
                         ("Carrot Orange", CARROT_ORANGE), ("Coal Black", COAL_BLACK)]:
        print(f"  {name:15}: {describe_color(color)}")

    print("\nColor Mixing Demo:")
    mixed = mix_colors(RED, BLUE, 0.5)
    print(f"  Red + Blue (50/50): {describe_color(mixed)}")

    mixed2 = mix_colors(RED, GREEN, 0.5)
    print(f"  Red + Green (50/50): {describe_color(mixed2)}")

    print("\nDarkening Demo:")
    dark_red = darken_color(RED, 0.5)
    print(f"  Dark Red: {describe_color(dark_red)}")

    print("\nGradient from Black to White (5 steps):")
    gradient = create_gradient(BLACK, WHITE, 5)
    for i, color in enumerate(gradient):
        bar = "█" * int(color_brightness(color) / 32)
        print(f"  Step {i}: {describe_color(color)} {bar}")

    print("\nLight vs Dark:")
    for name, color in [("White", WHITE), ("Black", BLACK),
                         ("Yellow", YELLOW), ("Navy Blue", (0, 0, 128))]:
        light = is_light_color(color)
        print(f"  {name:12}: {'Light' if light else 'Dark'} "
              f"(brightness={color_brightness(color):.0f})")


if __name__ == "__main__":
    main()

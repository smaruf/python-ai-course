"""
Drawing a Snowperson with Pygame
=================================

This module builds a snowperson step by step using pygame's drawing functions.
We start with the highest-level function and work our way down to the details.

Learning Objectives:
- Draw circles using pygame.draw.circle
- Draw rectangles using pygame.draw.rect
- Compose complex drawings from simple shapes
- Use coordinates to position shapes relative to each other
- Understand the top-down design approach in graphics programming

Key Pygame Drawing Functions:
- pygame.draw.circle(surface, color, center, radius) - draw a filled circle
- pygame.draw.circle(surface, color, center, radius, width) - draw circle outline
- pygame.draw.rect(surface, color, (x, y, w, h)) - draw a filled rectangle
- pygame.draw.rect(surface, color, (x, y, w, h), width) - draw rectangle outline

Snowperson Structure:
    ┌──────────┐  ← eyebrow left
    │  ●    ●  │  ← eyes
    │    ◆     │  ← nose (orange/carrot)
    │  ━━━━━   │  ← mouth
    └──────────┘  HEAD (circle)

    ┌──────────────┐
    │   ●  ●  ●    │  ← buttons
    └──────────────┘  MIDDLE (larger circle)

    ┌──────────────────┐
    │                  │  BOTTOM (largest circle)
    └──────────────────┘

Video Timestamps:
- 34:40 - Highest level snowperson drawing function
- 39:33 - Drawing the head
- 49:01 - Drawing a circular nose and eyes
- 57:31 - Adding a rectangular mouth and eyebrows
- 1:06:30 - Drawing the snowperson middle and bottom
- 1:18:39 - The snow is yellow (color discussion)
"""

# Color constants for the snowperson
SNOW_WHITE = (240, 240, 255)
SNOW_OUTLINE = (180, 180, 200)
CARROT_ORANGE = (255, 140, 0)
COAL_BLACK = (20, 20, 20)
SCARF_RED = (200, 0, 0)
SKY_BLUE = (135, 206, 250)
YELLOW_SNOW = (255, 255, 100)
BACKGROUND_COLOR = SKY_BLUE

# Snowperson proportions
HEAD_RADIUS = 60
MIDDLE_RADIUS = 85
BOTTOM_RADIUS = 110

# Eye properties
EYE_RADIUS = 8
EYE_OFFSET_X = 22   # Horizontal distance from center
EYE_OFFSET_Y = 15   # Vertical distance above center

# Nose properties
NOSE_RADIUS = 7
NOSE_OFFSET_Y = 5   # Below center

# Mouth properties
MOUTH_WIDTH = 40
MOUTH_HEIGHT = 8
MOUTH_OFFSET_Y = 22  # Below center

# Eyebrow properties
EYEBROW_WIDTH = 20
EYEBROW_HEIGHT = 5
EYEBROW_OFFSET_Y = 30  # Above center

# Button properties
BUTTON_RADIUS = 7
BUTTON_SPACING = 20  # Vertical spacing between buttons


def get_snowperson_parts(cx, cy):
    """
    Calculate the center positions of all snowperson body parts.

    The snowperson is built from bottom up:
    - Bottom circle at (cx, cy)
    - Middle circle sitting on top of bottom
    - Head sitting on top of middle

    Args:
        cx: x-coordinate of the snowperson's center (bottom circle center)
        cy: y-coordinate of the snowperson's center (bottom circle center)

    Returns:
        Dictionary with positions for 'bottom', 'middle', 'head'
    """
    bottom_center = (cx, cy)
    middle_center = (cx, cy - BOTTOM_RADIUS - MIDDLE_RADIUS + 15)
    head_center = (cx, middle_center[1] - MIDDLE_RADIUS - HEAD_RADIUS + 15)

    return {
        'bottom': bottom_center,
        'middle': middle_center,
        'head': head_center,
    }


def get_eye_positions(head_cx, head_cy):
    """
    Calculate the positions of the snowperson's eyes.

    Args:
        head_cx: x-coordinate of the head center
        head_cy: y-coordinate of the head center

    Returns:
        Tuple of ((left_eye_x, left_eye_y), (right_eye_x, right_eye_y))
    """
    left_eye = (head_cx - EYE_OFFSET_X, head_cy - EYE_OFFSET_Y)
    right_eye = (head_cx + EYE_OFFSET_X, head_cy - EYE_OFFSET_Y)
    return (left_eye, right_eye)


def get_nose_position(head_cx, head_cy):
    """
    Calculate the position of the snowperson's nose.

    Args:
        head_cx: x-coordinate of the head center
        head_cy: y-coordinate of the head center

    Returns:
        Tuple (nose_x, nose_y)
    """
    return (head_cx, head_cy + NOSE_OFFSET_Y)


def get_mouth_rect(head_cx, head_cy):
    """
    Calculate the rectangle for the snowperson's mouth.

    Returns the (x, y, width, height) of the mouth rectangle,
    where (x, y) is the top-left corner.

    Args:
        head_cx: x-coordinate of the head center
        head_cy: y-coordinate of the head center

    Returns:
        Tuple (x, y, width, height) for the mouth rectangle
    """
    x = head_cx - MOUTH_WIDTH // 2
    y = head_cy + MOUTH_OFFSET_Y
    return (x, y, MOUTH_WIDTH, MOUTH_HEIGHT)


def get_eyebrow_rects(head_cx, head_cy):
    """
    Calculate the rectangles for the snowperson's eyebrows.

    Args:
        head_cx: x-coordinate of the head center
        head_cy: y-coordinate of the head center

    Returns:
        Tuple of two (x, y, width, height) tuples for left and right eyebrows
    """
    left_x = head_cx - EYE_OFFSET_X - EYEBROW_WIDTH // 2
    right_x = head_cx + EYE_OFFSET_X - EYEBROW_WIDTH // 2
    y = head_cy - EYEBROW_OFFSET_Y

    left_eyebrow = (left_x, y, EYEBROW_WIDTH, EYEBROW_HEIGHT)
    right_eyebrow = (right_x, y, EYEBROW_WIDTH, EYEBROW_HEIGHT)
    return (left_eyebrow, right_eyebrow)


def get_button_positions(middle_cx, middle_cy):
    """
    Calculate the positions of the buttons on the snowperson's middle body.

    Args:
        middle_cx: x-coordinate of the middle body center
        middle_cy: y-coordinate of the middle body center

    Returns:
        List of (x, y) tuples for each button
    """
    return [
        (middle_cx, middle_cy - BUTTON_SPACING),
        (middle_cx, middle_cy),
        (middle_cx, middle_cy + BUTTON_SPACING),
    ]


def draw_head(surface, head_cx, head_cy, snow_color=SNOW_WHITE):
    """
    Draw the snowperson's head (a circle).

    Args:
        surface: pygame Surface to draw on
        head_cx: x-coordinate of the head center
        head_cy: y-coordinate of the head center
        snow_color: Color for the snow (default SNOW_WHITE)
    """
    import pygame
    pygame.draw.circle(surface, snow_color, (head_cx, head_cy), HEAD_RADIUS)
    pygame.draw.circle(surface, SNOW_OUTLINE, (head_cx, head_cy), HEAD_RADIUS, 2)


def draw_eyes(surface, head_cx, head_cy):
    """
    Draw the snowperson's eyes (two coal-black circles).

    Args:
        surface: pygame Surface to draw on
        head_cx: x-coordinate of the head center
        head_cy: y-coordinate of the head center
    """
    import pygame
    left_eye, right_eye = get_eye_positions(head_cx, head_cy)
    pygame.draw.circle(surface, COAL_BLACK, left_eye, EYE_RADIUS)
    pygame.draw.circle(surface, COAL_BLACK, right_eye, EYE_RADIUS)


def draw_nose(surface, head_cx, head_cy):
    """
    Draw the snowperson's nose (an orange carrot circle).

    Args:
        surface: pygame Surface to draw on
        head_cx: x-coordinate of the head center
        head_cy: y-coordinate of the head center
    """
    import pygame
    nose_pos = get_nose_position(head_cx, head_cy)
    pygame.draw.circle(surface, CARROT_ORANGE, nose_pos, NOSE_RADIUS)


def draw_mouth(surface, head_cx, head_cy):
    """
    Draw the snowperson's mouth (a dark rectangle).

    Args:
        surface: pygame Surface to draw on
        head_cx: x-coordinate of the head center
        head_cy: y-coordinate of the head center
    """
    import pygame
    mouth_rect = get_mouth_rect(head_cx, head_cy)
    pygame.draw.rect(surface, COAL_BLACK, mouth_rect)


def draw_eyebrows(surface, head_cx, head_cy):
    """
    Draw the snowperson's eyebrows (two dark rectangles).

    Args:
        surface: pygame Surface to draw on
        head_cx: x-coordinate of the head center
        head_cy: y-coordinate of the head center
    """
    import pygame
    left_brow, right_brow = get_eyebrow_rects(head_cx, head_cy)
    pygame.draw.rect(surface, COAL_BLACK, left_brow)
    pygame.draw.rect(surface, COAL_BLACK, right_brow)


def draw_face(surface, head_cx, head_cy, snow_color=SNOW_WHITE):
    """
    Draw the complete face of the snowperson.

    Combines: head + eyes + nose + mouth + eyebrows.

    Args:
        surface: pygame Surface to draw on
        head_cx: x-coordinate of the head center
        head_cy: y-coordinate of the head center
        snow_color: Color for the snow (default SNOW_WHITE)
    """
    draw_head(surface, head_cx, head_cy, snow_color)
    draw_eyebrows(surface, head_cx, head_cy)
    draw_eyes(surface, head_cx, head_cy)
    draw_nose(surface, head_cx, head_cy)
    draw_mouth(surface, head_cx, head_cy)


def draw_middle(surface, middle_cx, middle_cy, snow_color=SNOW_WHITE):
    """
    Draw the snowperson's middle body section.

    Args:
        surface: pygame Surface to draw on
        middle_cx: x-coordinate of the middle body center
        middle_cy: y-coordinate of the middle body center
        snow_color: Color for the snow (default SNOW_WHITE)
    """
    import pygame
    pygame.draw.circle(surface, snow_color, (middle_cx, middle_cy), MIDDLE_RADIUS)
    pygame.draw.circle(surface, SNOW_OUTLINE, (middle_cx, middle_cy), MIDDLE_RADIUS, 2)

    # Draw buttons
    for btn_pos in get_button_positions(middle_cx, middle_cy):
        pygame.draw.circle(surface, COAL_BLACK, btn_pos, BUTTON_RADIUS)


def draw_bottom(surface, bottom_cx, bottom_cy, snow_color=SNOW_WHITE):
    """
    Draw the snowperson's bottom body section.

    Args:
        surface: pygame Surface to draw on
        bottom_cx: x-coordinate of the bottom body center
        bottom_cy: y-coordinate of the bottom body center
        snow_color: Color for the snow (default SNOW_WHITE)
    """
    import pygame
    pygame.draw.circle(surface, snow_color, (bottom_cx, bottom_cy), BOTTOM_RADIUS)
    pygame.draw.circle(surface, SNOW_OUTLINE, (bottom_cx, bottom_cy), BOTTOM_RADIUS, 2)


def draw_snowperson(surface, cx, cy, snow_color=SNOW_WHITE):
    """
    Draw a complete snowperson centered at (cx, cy).

    This is the highest-level function that draws all parts.
    The (cx, cy) position is the center of the bottom body.

    Args:
        surface: pygame Surface to draw on
        cx: x-coordinate of the snowperson's horizontal center
        cy: y-coordinate of the bottom body circle's center
        snow_color: Color of the snow (try YELLOW_SNOW for fun!)
    """
    parts = get_snowperson_parts(cx, cy)

    # Draw from bottom to top so head appears on top
    bottom_cx, bottom_cy = parts['bottom']
    middle_cx, middle_cy = parts['middle']
    head_cx, head_cy = parts['head']

    draw_bottom(surface, bottom_cx, bottom_cy, snow_color)
    draw_middle(surface, middle_cx, middle_cy, snow_color)
    draw_face(surface, head_cx, head_cy, snow_color)


def main():
    """
    Main demonstration: draw a snowperson in a pygame window.
    """
    WINDOW_WIDTH = 500
    WINDOW_HEIGHT = 700
    WINDOW_TITLE = "Snowperson Drawing"

    try:
        import pygame
    except ImportError:
        print("pygame is not installed. Run: pip install pygame")
        print("\nDemonstrating snowperson coordinates without display:")

        cx, cy = 250, 580
        parts = get_snowperson_parts(cx, cy)
        print(f"\nSnowperson centered at x={cx}, bottom at y={cy}:")
        print(f"  Bottom body center: {parts['bottom']}")
        print(f"  Middle body center: {parts['middle']}")
        print(f"  Head center: {parts['head']}")

        head_cx, head_cy = parts['head']
        left_eye, right_eye = get_eye_positions(head_cx, head_cy)
        print(f"\nFace details (head at {parts['head']}):")
        print(f"  Left eye: {left_eye}")
        print(f"  Right eye: {right_eye}")
        print(f"  Nose: {get_nose_position(head_cx, head_cy)}")
        print(f"  Mouth rect: {get_mouth_rect(head_cx, head_cy)}")
        left_brow, right_brow = get_eyebrow_rects(head_cx, head_cy)
        print(f"  Left eyebrow: {left_brow}")
        print(f"  Right eyebrow: {right_brow}")
        return

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw sky background
        screen.fill(BACKGROUND_COLOR)

        # Draw ground (yellow snow - the classic joke!)
        import pygame as pg
        pg.draw.rect(screen, YELLOW_SNOW, (0, WINDOW_HEIGHT - 80, WINDOW_WIDTH, 80))

        # Draw the snowperson
        draw_snowperson(screen, WINDOW_WIDTH // 2, WINDOW_HEIGHT - 80 - BOTTOM_RADIUS + 30)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    print("=" * 60)
    print("DRAWING A SNOWPERSON")
    print("=" * 60)
    print("\nBuilding a snowperson from simple shapes:")
    print("  - Head: circle (radius 60)")
    print("  - Eyes: two small circles")
    print("  - Nose: orange circle")
    print("  - Mouth: dark rectangle")
    print("  - Eyebrows: two dark rectangles")
    print("  - Middle body: larger circle with buttons")
    print("  - Bottom body: largest circle")
    print("\nStarting pygame window...")
    main()

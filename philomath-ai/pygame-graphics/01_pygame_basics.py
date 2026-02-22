"""
Pygame Basics - Introduction to Graphics in Python
====================================================

This module introduces pygame, a popular Python library for creating 2D games
and graphics applications. Pygame provides tools for drawing shapes, handling
colors, creating windows, and much more.

Learning Objectives:
- Import and initialize pygame
- Create a window (surface) with a title
- Understand the pygame coordinate system
- Draw a basic black rectangle on a colored surface
- Use pygame's event loop to keep the window open
- Properly close a pygame application

Key Concepts:
- Surface: A 2-D image area where you can draw shapes and images
- Display: The visible window shown to the user
- Event loop: The main loop that listens for user input and updates the screen
- Coordinates: (x, y) where (0, 0) is the TOP-LEFT corner
- Fill: Painting the entire surface with one color
- Rect: A rectangle defined by (x, y, width, height)

Coordinate System:
    (0,0) ──────────────────► x increases rightward
      │
      │
      │
      ▼
    y increases downward

This is DIFFERENT from math graphs where y increases upward!
"""

# Constants for window dimensions and colors
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500
WINDOW_TITLE = "Pygame Basics"

# Color constants (R, G, B) - each value is 0-255
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

# Rectangle dimensions for the demo
RECT_X = 100
RECT_Y = 100
RECT_WIDTH = 300
RECT_HEIGHT = 300


def get_window_dimensions():
    """
    Return the default window dimensions.

    Returns:
        Tuple of (width, height)
    """
    return (WINDOW_WIDTH, WINDOW_HEIGHT)


def get_rect_params():
    """
    Return the parameters for the demo rectangle.

    Returns:
        Tuple of (x, y, width, height)
    """
    return (RECT_X, RECT_Y, RECT_WIDTH, RECT_HEIGHT)


def is_point_in_rect(px, py, rx, ry, rw, rh):
    """
    Check if a point (px, py) is inside a rectangle.

    The rectangle is defined by its top-left corner (rx, ry)
    and its dimensions (rw, rh).

    Args:
        px: x-coordinate of the point
        py: y-coordinate of the point
        rx: x-coordinate of the rectangle's top-left corner
        ry: y-coordinate of the rectangle's top-left corner
        rw: width of the rectangle
        rh: height of the rectangle

    Returns:
        True if the point is inside or on the rectangle, False otherwise
    """
    return rx <= px <= rx + rw and ry <= py <= ry + rh


def get_rect_center(rx, ry, rw, rh):
    """
    Calculate the center point of a rectangle.

    Args:
        rx: x-coordinate of the rectangle's top-left corner
        ry: y-coordinate of the rectangle's top-left corner
        rw: width of the rectangle
        rh: height of the rectangle

    Returns:
        Tuple (cx, cy) representing the center coordinates
    """
    return (rx + rw // 2, ry + rh // 2)


def main():
    """
    Main demonstration: create a pygame window with a black rectangle.

    Demonstrates:
    1. pygame initialization
    2. Creating a window surface
    3. Filling the surface with white
    4. Drawing a black rectangle
    5. Running the event loop until the window is closed
    """
    try:
        import pygame
    except ImportError:
        print("pygame is not installed. Run: pip install pygame")
        print("This module requires pygame for visual output.")
        print("\nDemonstrating concepts without display:\n")
        print(f"Window size: {WINDOW_WIDTH} x {WINDOW_HEIGHT}")
        print(f"Rectangle at ({RECT_X}, {RECT_Y}) with size {RECT_WIDTH}x{RECT_HEIGHT}")
        cx, cy = get_rect_center(RECT_X, RECT_Y, RECT_WIDTH, RECT_HEIGHT)
        print(f"Rectangle center: ({cx}, {cy})")
        print(f"Point (250, 250) in rect? {is_point_in_rect(250, 250, RECT_X, RECT_Y, RECT_WIDTH, RECT_HEIGHT)}")
        return

    # Step 1: Initialize pygame
    # This sets up all pygame modules (display, sound, fonts, etc.)
    pygame.init()

    # Step 2: Create the window surface
    # pygame.display.set_mode returns a Surface object representing the window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    # Step 3: Set the window title
    pygame.display.set_caption(WINDOW_TITLE)

    # Step 4: Main game loop
    running = True
    while running:
        # Handle events (user input)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Step 5: Draw to the screen
        # Fill the background with white
        screen.fill(WHITE)

        # Draw a black rectangle using pygame.draw.rect
        # Parameters: surface, color, (x, y, width, height)
        pygame.draw.rect(screen, BLACK, (RECT_X, RECT_Y, RECT_WIDTH, RECT_HEIGHT))

        # Step 6: Update the display
        # This shows everything we drew to the screen
        pygame.display.flip()

    # Step 7: Clean up
    pygame.quit()


if __name__ == "__main__":
    print("=" * 60)
    print("PYGAME BASICS - Introduction to Graphics")
    print("=" * 60)
    print("\nThis module introduces pygame for creating graphics in Python.")
    print(f"Window: {WINDOW_WIDTH} x {WINDOW_HEIGHT} pixels")
    print(f"Rectangle: ({RECT_X}, {RECT_Y}) size {RECT_WIDTH}x{RECT_HEIGHT}")
    print("\nCoordinate System:")
    print("  (0,0) is TOP-LEFT corner")
    print("  x increases rightward")
    print("  y increases DOWNWARD (opposite of math!)")
    print("\nStarting pygame window...")
    main()

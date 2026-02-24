# Pygame Graphics - An Intro to Graphics in Python

> **Part of [Philomath AI](../README.md)** | [Python AI Course](../../README.md)  
> See also: [← 2-D Lists](../2d-lists/) (prerequisite for Game of Life) | [Genome Algorithms](../genome_algorithms/) | [Monte Carlo Simulation](../monte-carlo/)

Welcome to the **Pygame Graphics** module, implementing concepts from "Programming for Lovers in Python: An Intro to Graphics" by Phillip Compeau.

## 📚 Module Overview

This module introduces **pygame**, a popular Python library for creating 2D graphics and games. We build up from basic window creation to drawing a complete snowperson, and finally to visualizing Conway's Game of Life as a beautiful animated grid of circles.

Each file includes:
- **Clear explanations** of pygame concepts and the RGB color model
- **Progressive implementations** from simple shapes to complex drawings
- **Pure-logic functions** that can be tested without a display
- **Visual demonstrations** when run with a pygame-enabled environment

## 🎯 Learning Objectives

By working through this module, you will master:

### Graphics Concepts
- **Pygame initialization**: Setting up the display and event loop
- **Coordinate system**: Understanding that (0,0) is the TOP-LEFT corner and y increases downward
- **RGB color model**: Mixing red, green, and blue light to create any color
- **Drawing shapes**: Circles and rectangles using `pygame.draw`
- **Animation**: Updating the display in a loop to create motion

### Programming Skills
- **Top-down design**: Breaking complex drawings into smaller functions
- **Coordinate math**: Calculating positions relative to a center point
- **2-D arrays**: Using grids to represent game state
- **Event loops**: Handling user input in interactive programs

### Fun Projects
- **Snowperson**: A classic drawing exercise demonstrating shape composition
- **Game of Life**: Visualizing Conway's cellular automaton with circular cells

## 📁 Directory Structure

```
pygame-graphics/
├── README.md                              # This file
├── 01_pygame_basics.py                   # pygame setup, surfaces, coordinate system
├── 02_rgb_colors.py                      # RGB color model, color mixing and utilities
├── 03_snowperson.py                      # Drawing a snowperson from simple shapes
├── 04_game_of_life_visualization.py      # Animated Game of Life: age colours, mouse drawing
├── 05_krypton_simulation.py             # Multi-faction Game of Life (Krypton theme)
└── test_all.py                            # Test suite (no display required)
```

## 🚀 Quick Start

### Installation

```bash
pip install pygame
```

### Running Examples

Each module can be run standalone:

```bash
cd pygame-graphics

# Learn about pygame surfaces and coordinates
python 01_pygame_basics.py

# Explore the RGB color model
python 02_rgb_colors.py

# Draw a snowperson
python 03_snowperson.py

# Visualize the Game of Life
python 04_game_of_life_visualization.py

# Run the multi-faction Krypton Chronicles simulation
python 05_krypton_simulation.py
```

### Running Tests

The test suite works without a display:

```bash
python test_all.py
```

## 📖 Key Topics

### 1. Pygame Basics (01)

Setting up a pygame window and drawing your first rectangle.

```python
import pygame

pygame.init()
screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption("My Window")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((255, 255, 255))                    # White background
    pygame.draw.rect(screen, (0, 0, 0), (100, 100, 300, 300))  # Black rectangle
    pygame.display.flip()

pygame.quit()
```

**Coordinate System:**
```
(0,0) ──────────────────► x increases rightward
  │
  │
  ▼
y increases DOWNWARD (opposite of math graphs!)
```

### 2. RGB Color Model (02)

Every pixel on screen is a mix of Red, Green, and Blue light:

| Color    | R   | G   | B   |
|----------|-----|-----|-----|
| Black    | 0   | 0   | 0   |
| White    | 255 | 255 | 255 |
| Red      | 255 | 0   | 0   |
| Green    | 0   | 255 | 0   |
| Blue     | 0   | 0   | 255 |
| Yellow   | 255 | 255 | 0   |
| Cyan     | 0   | 255 | 255 |
| Magenta  | 255 | 0   | 255 |

```python
# Mix two colors
def mix_colors(color1, color2, ratio=0.5):
    r = int(color1[0] * ratio + color2[0] * (1 - ratio))
    g = int(color1[1] * ratio + color2[1] * (1 - ratio))
    b = int(color1[2] * ratio + color2[2] * (1 - ratio))
    return (r, g, b)
```

### 3. Drawing a Snowperson (03)

Building a complex drawing from simple shapes using top-down design:

```python
def draw_snowperson(surface, cx, cy):
    """Draw a complete snowperson at (cx, cy)."""
    draw_bottom(surface, cx, cy)
    draw_middle(surface, cx, cy - 195)
    draw_face(surface, cx, cy - 350)

def draw_face(surface, cx, cy):
    """Draw the face with eyes, nose, mouth, and eyebrows."""
    draw_head(surface, cx, cy)       # Big circle
    draw_eyebrows(surface, cx, cy)   # Two rectangles
    draw_eyes(surface, cx, cy)       # Two small circles
    draw_nose(surface, cx, cy)       # Orange circle
    draw_mouth(surface, cx, cy)      # Dark rectangle
```

**Pygame drawing functions:**
```python
# Draw a filled circle
pygame.draw.circle(surface, color, (cx, cy), radius)

# Draw a circle outline
pygame.draw.circle(surface, color, (cx, cy), radius, width)

# Draw a filled rectangle
pygame.draw.rect(surface, color, (x, y, width, height))
```

### 4. Game of Life Visualization (04)

Visualizing Conway's Game of Life with animated circular cells.  Builds directly on the console implementation in [2d-lists/06_game_of_life.py](../2d-lists/06_game_of_life.py).

**Core drawing** (original, closed to modification):
```python
def draw_board(surface, board, cell_radius=CELL_RADIUS, cell_size=CELL_SIZE,
               alive_color=CELL_ALIVE_COLOR, dead_color=CELL_DEAD_COLOR):
    """Draw cells as circles: green=alive, dark=dead."""
    for row in range(len(board)):
        for col in range(len(board[0])):
            center = cell_to_pixel(row, col)
            color = alive_color if board[row][col] == 1 else dead_color
            pygame.draw.circle(surface, color, center, CELL_RADIUS)
```

**Age-based colouring** (extension, open for new behaviour):
```python
# Track how long each cell has been alive
age_board = create_age_board(BOARD_ROWS, BOARD_COLS)
update_age_board(board, age_board)   # call once per generation

# Render alive cells coloured by age (green → yellow → white)
draw_board_with_age(surface, board, age_board)
```

**Controls in the pygame window:**
| Key / Action | Effect |
|---|---|
| `SPACE` | Pause / Resume animation |
| `R` | Reset to R pentomino |
| `A` | Toggle age-based cell colouring on/off |
| `↑` / `↓` | Increase / decrease animation speed (20–500 ms/gen) |
| Click | Toggle a single cell |
| Drag | Paint live cells (draw mode) |
| `ESC` | Quit |

### 5. Krypton Chronicles – Multi-Faction Game of Life (05)

A themed cellular automaton where cells belong to four factions, each colour-coded:

| State | Color | Description |
|-------|--------|-------------|
| Kryptonian | 🔵 Blue | Superman and Kryptonian survivors |
| Earthian Ally | 🟢 Green | Bonded earthians who protect Kryptonians |
| Earthian Enemy | 🔴 Red | Villains seeking to destroy them |
| Evil / Corrupted | 🟣 Purple | Kryptonian turned evil or corrupted agent |

**Key rules (themed around the story):**
- A Kryptonian overwhelmed by 4+ enemies **turns evil**
- A Kryptonian shielded by allies **survives**
- An empty cell with 1 Kryptonian + 2 allies **births a new Kryptonian** (favorable race)
- Evil **spreads** to empty cells with 3+ evil neighbours

```python
# The "favorable race" birth rule
if state == EMPTY:
    if kryp_count >= 1 and ally_count >= 2:
        new_board[r][c] = KRYPTONIAN   # new hope!
```

**Controls in the pygame window:**
- `SPACE` - Pause/Resume
- `R` - Reset scenario
- `ESC` - Quit

## 🎮 Video Code-Alongs

This module accompanies the **"An Intro to Graphics in Python"** Philomath code-along:

| Timestamp | Topic |
|-----------|-------|
| 00:00 | Start screen |
| 15:00 | Importing pygame |
| 16:52 | RGB color model |
| 22:25 | Creating a pygame surface and black rectangle |
| 30:27 | Graphics coordinates |
| 34:40 | Highest level snowperson drawing function |
| 39:33 | Drawing the head |
| 49:01 | Drawing a circular nose and eyes |
| 57:31 | Adding a rectangular mouth and eyebrows |
| 1:06:30 | Drawing the snowperson middle and bottom |
| 1:18:39 | The snow is yellow |
| 1:25:24 | Drawing a Game of Life board |
| 1:47:34 | Visualizing the R pentomino |
| 1:55:01 | Prettifying the visualization with circular cells |
| 2:02:27 | Scaling down the circle size to separate them |
| 2:08:01 | Changing colors, looking ahead, and happy coding 🫶 |

Part of **Chapter 3** of *Programming for Lovers* on "Discovering a Self-Replicating Cellular Automaton".

### Code-Along References
- [An Intro to Graphics in Python](https://programmingforlovers.com/chap...)
- [Drawing the Game of Life](https://programmingforlovers.com/chap...)

## 🌍 Real-World Applications

### Pygame and 2D Graphics
These skills are used in:
- **Game Development**: Platformers, puzzle games, arcade games
- **Data Visualization**: Custom interactive charts and animations
- **Simulations**: Scientific simulations with visual output
- **Education**: Interactive demos for teaching math and science
- **Generative Art**: Creating algorithmic art and animations

### RGB Color Model
Used in:
- **Web Design**: CSS colors (`rgb(255, 0, 0)` for red)
- **Image Processing**: Photo editing, filtering, compositing
- **Digital Art**: Graphic design, illustration, animation
- **Hardware**: LED displays, monitors, projectors
- **Photography**: Color correction, white balance

## 📚 Additional Resources

- [Pygame Official Documentation](https://www.pygame.org/docs/)
- [Pygame Tutorial (Real Python)](https://realpython.com/pygame-a-primer/)
- [Conway's Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life)
- [RGB Color Model](https://en.wikipedia.org/wiki/RGB_color_model)
- [Programming for Lovers](https://programmingforlovers.com)

## 🎓 Course Reference

Part of **Chapter 3** of *Programming for Lovers in Python* by Phillip Compeau:

**"Discovering a Self-Replicating Cellular Automaton"**

This module covers multi-dimensional arrays, drawing a face, and drawing The Game of Life.

## 📄 License

See the main repository [LICENSE](../../LICENSE) file.

## 🙏 Acknowledgments

- **Phillip Compeau** - Course creator and educator at Carnegie Mellon University
- **Programming for Lovers** - Open online course at https://programmingforlovers.com
- **John Conway** - Mathematician who invented the Game of Life (1937-2020)
- **The Pygame community** - For building and maintaining an excellent library

---

**Ready to bring your code to life with graphics? Let's dive in! 🎨🖥️❄️**

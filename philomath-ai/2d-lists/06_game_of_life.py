"""
Conway's Game of Life - Cellular Automaton
===========================================

Conway's Game of Life is a cellular automaton invented by mathematician John Conway in 1970.
Despite its simple rules, it produces incredibly complex behavior including self-replicating patterns.
The R pentomino is a famous small pattern that evolves for over 1000 generations.

Learning Objectives:
- Implement Conway's Game of Life rules
- Work with cellular automata
- Count neighbors in a 2-D grid
- Update grid state based on rules
- Visualize the R pentomino pattern
- Understand emergent complexity from simple rules

Key Concepts:
- Cellular automaton: Grid where cells have states that evolve over time
- Rules are applied simultaneously to all cells
- Need two grids: current state and next state
- Each cell has 8 neighbors (including diagonals)
- Simple rules can create complex, unpredictable behavior
- Self-replication: Patterns that create copies of themselves

Game of Life Rules:
1. Birth: Dead cell with exactly 3 live neighbors becomes alive
2. Survival: Live cell with 2 or 3 live neighbors stays alive
3. Death: All other cells die (or stay dead)
"""

import time
import os
import random


def create_empty_grid(rows, cols):
    """
    Create an empty grid (all dead cells).
    
    Args:
        rows: Number of rows
        cols: Number of columns
    
    Returns:
        2-D list filled with 0 (dead cells)
    """
    return [[0 for _ in range(cols)] for _ in range(rows)]


def count_neighbors(grid, row, col):
    """
    Count the number of live neighbors for a cell.
    
    A cell has 8 neighbors: up, down, left, right, and 4 diagonals.
    
    Args:
        grid: 2-D list representing the grid
        row: Row of the cell
        col: Column of the cell
    
    Returns:
        Number of live neighbors (0-8)
    """
    rows = len(grid)
    cols = len(grid[0])
    count = 0
    
    # Check all 8 directions
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            # Skip the cell itself
            if dr == 0 and dc == 0:
                continue
            
            # Calculate neighbor position
            new_row = row + dr
            new_col = col + dc
            
            # Check bounds
            if 0 <= new_row < rows and 0 <= new_col < cols:
                if grid[new_row][new_col] == 1:
                    count += 1
    
    return count


def apply_rules(grid):
    """
    Apply Game of Life rules to generate the next generation.
    
    Rules:
    - Birth: Dead cell (0) with exactly 3 live neighbors becomes alive (1)
    - Survival: Live cell (1) with 2 or 3 live neighbors stays alive
    - Death: All other cells become dead
    
    Args:
        grid: Current state of the grid
    
    Returns:
        New grid representing the next generation
    """
    rows = len(grid)
    cols = len(grid[0])
    
    # Create new grid for next generation
    new_grid = create_empty_grid(rows, cols)
    
    # Apply rules to each cell
    for i in range(rows):
        for j in range(cols):
            neighbors = count_neighbors(grid, i, j)
            
            if grid[i][j] == 1:
                # Cell is alive
                if neighbors == 2 or neighbors == 3:
                    new_grid[i][j] = 1  # Survival
                else:
                    new_grid[i][j] = 0  # Death (overpopulation or loneliness)
            else:
                # Cell is dead
                if neighbors == 3:
                    new_grid[i][j] = 1  # Birth
                else:
                    new_grid[i][j] = 0  # Stay dead
    
    return new_grid


def place_pattern(grid, pattern, start_row, start_col):
    """
    Place a pattern on the grid at the specified position.
    
    Args:
        grid: The grid to place the pattern on
        pattern: 2-D list representing the pattern (1 = alive, 0 = dead)
        start_row: Row to start placing the pattern
        start_col: Column to start placing the pattern
    """
    for i in range(len(pattern)):
        for j in range(len(pattern[i])):
            if pattern[i][j] == 1:
                grid[start_row + i][start_col + j] = 1


def create_r_pentomino():
    """
    Create the R pentomino pattern.
    
    The R pentomino is a small 5-cell pattern that evolves chaotically
    for over 1000 generations before stabilizing.
    
    Pattern shape:
      .##
      ##.
      .#.
    
    Returns:
        2-D list representing the R pentomino
    """
    return [
        [0, 1, 1],
        [1, 1, 0],
        [0, 1, 0]
    ]


def create_glider():
    """
    Create a glider pattern.
    
    A glider is a small pattern that moves diagonally across the grid.
    
    Pattern shape:
      .#.
      ..#
      ###
    
    Returns:
        2-D list representing a glider
    """
    return [
        [0, 1, 0],
        [0, 0, 1],
        [1, 1, 1]
    ]


def create_blinker():
    """
    Create a blinker pattern (period-2 oscillator).
    
    Pattern shape:
      ###
    
    Returns:
        2-D list representing a blinker
    """
    return [
        [1, 1, 1]
    ]


def create_block():
    """
    Create a block pattern (still life).
    
    Pattern shape:
      ##
      ##
    
    Returns:
        2-D list representing a block
    """
    return [
        [1, 1],
        [1, 1]
    ]


def count_neighbors_toroidal(grid, row, col):
    """
    Count live neighbors using toroidal (wrapping) boundary conditions.

    Cells at the edges wrap around to the opposite edge, so the grid
    behaves like the surface of a donut with no boundary effects.

    Args:
        grid: 2-D list representing the grid
        row: Row of the cell
        col: Column of the cell

    Returns:
        Number of live neighbors (0-8)
    """
    rows = len(grid)
    cols = len(grid[0])
    count = 0

    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            new_row = (row + dr) % rows  # Wrap around vertically
            new_col = (col + dc) % cols  # Wrap around horizontally
            if grid[new_row][new_col] == 1:
                count += 1

    return count


def apply_rules_toroidal(grid):
    """
    Apply Game of Life rules with toroidal (wrapping) boundary conditions.

    Uses the same birth/survival/death rules as apply_rules(), but cells
    at the edges treat the opposite edge as their neighbor instead of the
    boundary being treated as dead space.

    Args:
        grid: Current state of the grid

    Returns:
        New grid representing the next generation
    """
    rows = len(grid)
    cols = len(grid[0])
    new_grid = create_empty_grid(rows, cols)

    for i in range(rows):
        for j in range(cols):
            neighbors = count_neighbors_toroidal(grid, i, j)
            if grid[i][j] == 1:
                new_grid[i][j] = 1 if neighbors in (2, 3) else 0
            else:
                new_grid[i][j] = 1 if neighbors == 3 else 0

    return new_grid


def create_random_grid(rows, cols, density=0.3, seed=None):
    """
    Create a grid with randomly placed live cells.

    Args:
        rows: Number of rows
        cols: Number of columns
        density: Probability (0.0-1.0) that any given cell starts alive
        seed: Optional random seed for reproducibility

    Returns:
        2-D list with cells randomly set to 0 or 1
    """
    if seed is not None:
        random.seed(seed)
    return [[1 if random.random() < density else 0 for _ in range(cols)]
            for _ in range(rows)]


def print_grid(grid, generation=None):
    """
    Print the grid in a readable format.
    
    Args:
        grid: 2-D list to print
        generation: Optional generation number to display
    """
    if generation is not None:
        print(f"\n=== Generation {generation} ===")
    
    for row in grid:
        for cell in row:
            if cell == 1:
                print('█', end=' ')  # Alive cell
            else:
                print('·', end=' ')  # Dead cell
        print()


def count_living_cells(grid):
    """
    Count the total number of living cells in the grid.
    
    Args:
        grid: 2-D list representing the grid
    
    Returns:
        Number of living cells
    """
    return sum(sum(row) for row in grid)


def simulate_game_of_life(grid, generations, delay=0.1, clear_screen=True):
    """
    Simulate the Game of Life for a specified number of generations.
    
    Args:
        grid: Initial state of the grid
        generations: Number of generations to simulate
        delay: Delay between generations in seconds
        clear_screen: Whether to clear screen between generations
    """
    current_grid = grid
    
    for gen in range(generations):
        if clear_screen:
            os.system('clear' if os.name == 'posix' else 'cls')
        
        print_grid(current_grid, gen)
        print(f"Living cells: {count_living_cells(current_grid)}")
        
        if gen < generations - 1:
            current_grid = apply_rules(current_grid)
            time.sleep(delay)
    
    return current_grid


def demonstrate_r_pentomino():
    """
    Demonstrate the R pentomino pattern.
    
    This is the main demonstration from the video!
    """
    print("=" * 70)
    print("R PENTOMINO - Famous Chaotic Pattern")
    print("=" * 70)
    print("\nThe R pentomino is a small 5-cell pattern that evolves")
    print("chaotically for over 1000 generations before stabilizing.")
    print("\nInitial pattern:")
    print("  .██")
    print("  ██.")
    print("  .█.")
    print("\nStarting simulation...")
    print("(Press Ctrl+C to stop early)")
    print("=" * 70)
    
    # Create a large grid
    grid = create_empty_grid(40, 60)
    
    # Place R pentomino in the center
    r_pentomino = create_r_pentomino()
    place_pattern(grid, r_pentomino, 18, 28)
    
    # Simulate for 50 generations (not 1000+ for demo purposes)
    try:
        simulate_game_of_life(grid, 50, delay=0.2, clear_screen=False)
    except KeyboardInterrupt:
        print("\n\nSimulation stopped by user.")
    
    print("\n" + "=" * 70)
    print("The R pentomino continues to evolve for many more generations!")
    print("It reaches a stable state after 1103 generations.")
    print("=" * 70)


def demonstrate_simple_patterns():
    """
    Demonstrate some simple patterns.
    """
    print("\n=== Simple Patterns ===\n")
    
    # Blinker (period-2 oscillator)
    print("1. Blinker (oscillates between horizontal and vertical):")
    grid = create_empty_grid(5, 5)
    place_pattern(grid, create_blinker(), 2, 1)
    
    print("\nGeneration 0:")
    print_grid(grid)
    
    print("\nGeneration 1:")
    grid = apply_rules(grid)
    print_grid(grid)
    
    print("\nGeneration 2:")
    grid = apply_rules(grid)
    print_grid(grid)
    print("(Back to original state)")
    
    # Block (still life)
    print("\n\n2. Block (never changes):")
    grid = create_empty_grid(4, 4)
    place_pattern(grid, create_block(), 1, 1)
    
    print("\nGeneration 0:")
    print_grid(grid)
    
    print("\nGeneration 1:")
    grid = apply_rules(grid)
    print_grid(grid)
    print("(Still the same)")
    
    # Glider (moves diagonally)
    print("\n\n3. Glider (moves diagonally):")
    grid = create_empty_grid(10, 10)
    place_pattern(grid, create_glider(), 1, 1)
    
    for gen in range(5):
        print(f"\nGeneration {gen}:")
        print_grid(grid)
        if gen < 4:
            grid = apply_rules(grid)


def demonstrate_rules():
    """
    Demonstrate each rule individually.
    """
    print("\n=== Demonstrating Game of Life Rules ===\n")
    
    # Rule 1: Birth
    print("Rule 1: BIRTH - Dead cell with exactly 3 neighbors becomes alive")
    grid = [
        [0, 1, 0],
        [1, 0, 1],
        [0, 0, 0]
    ]
    print("Before:")
    print_grid(grid)
    print("\nCenter cell (0) has 3 neighbors → will become alive")
    
    new_grid = apply_rules(grid)
    print("\nAfter:")
    print_grid(new_grid)
    
    # Rule 2: Survival
    print("\n\nRule 2: SURVIVAL - Live cell with 2-3 neighbors stays alive")
    grid = [
        [0, 1, 0],
        [1, 1, 0],
        [0, 0, 0]
    ]
    print("Before:")
    print_grid(grid)
    print("\nCenter cell (1) has 2 neighbors → will survive")
    
    new_grid = apply_rules(grid)
    print("\nAfter:")
    print_grid(new_grid)
    
    # Rule 3: Death by underpopulation
    print("\n\nRule 3a: DEATH - Live cell with < 2 neighbors dies (loneliness)")
    grid = [
        [0, 0, 0],
        [0, 1, 0],
        [0, 1, 0]
    ]
    print("Before:")
    print_grid(grid)
    print("\nTop live cell has 1 neighbor → will die")
    
    new_grid = apply_rules(grid)
    print("\nAfter:")
    print_grid(new_grid)
    
    # Rule 4: Death by overpopulation
    print("\n\nRule 3b: DEATH - Live cell with > 3 neighbors dies (overpopulation)")
    grid = [
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0]
    ]
    print("Before:")
    print_grid(grid)
    print("\nCenter cell (1) has 4 neighbors → will die")
    
    new_grid = apply_rules(grid)
    print("\nAfter:")
    print_grid(new_grid)


def demonstrate_toroidal():
    """
    Demonstrate the difference between flat and toroidal grids.

    A glider reaching the edge of a flat grid vanishes (dies at the boundary).
    On a toroidal grid it wraps around and keeps travelling indefinitely.
    """
    print("\n" + "=" * 70)
    print("ENHANCEMENT: TOROIDAL (WRAPPING) BOUNDARIES")
    print("=" * 70)
    print("\nOn a flat grid, a glider that reaches the edge disappears.")
    print("On a toroidal grid the edges wrap around — the glider loops forever.\n")

    size = 10

    # ── Flat grid: glider near the bottom-right edge ─────────────────────────
    print("Flat grid – glider placed near the bottom-right corner:")
    flat = create_empty_grid(size, size)
    place_pattern(flat, create_glider(), size - 4, size - 4)
    for gen in range(5):
        print(f"  Gen {gen}: {count_living_cells(flat)} alive")
        flat = apply_rules(flat)

    # ── Toroidal grid: same starting position ────────────────────────────────
    print("\nToroidal grid – same starting position (glider wraps):")
    torus = create_empty_grid(size, size)
    place_pattern(torus, create_glider(), size - 4, size - 4)
    for gen in range(5):
        print(f"  Gen {gen}: {count_living_cells(torus)} alive")
        torus = apply_rules_toroidal(torus)

    print("\nNotice: on the toroidal grid the glider is preserved across the edge.")

    # ── Random grid for a few steps ──────────────────────────────────────────
    print("\nRandom grid (density=0.35, seed=42) – 5 generations:")
    rgrid = create_random_grid(8, 12, density=0.35, seed=42)
    for gen in range(6):
        print(f"  Gen {gen}: {count_living_cells(rgrid)} alive")
        if gen < 5:
            rgrid = apply_rules_toroidal(rgrid)


def main():
    """
    Main demonstration function.
    """
    print("=" * 70)
    print("CONWAY'S GAME OF LIFE")
    print("Programming for Lovers in Python - Chapter 3")
    print("Cellular Automaton and Self-Replication")
    print("=" * 70)

    # Demonstrate the rules
    demonstrate_rules()

    # Show simple patterns
    demonstrate_simple_patterns()

    # Enhancement: toroidal grid and random initialisation
    demonstrate_toroidal()

    # Main event: R pentomino
    input("\nPress Enter to see the R pentomino simulation...")
    demonstrate_r_pentomino()

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS:")
    print("=" * 70)
    print("1. Simple rules can create complex behavior")
    print("2. Cells have 8 neighbors (including diagonals)")
    print("3. Rules: Birth (3), Survival (2-3), Death (otherwise)")
    print("4. Need TWO grids: current and next generation")
    print("5. Apply rules simultaneously to all cells")
    print("6. R pentomino: 5 cells → 1000+ generations of chaos")
    print("7. Self-replication emerges from simple rules!")
    print("8. Toroidal grid: wrap edges to eliminate boundary effects")
    print("9. Random initialisation: explore beyond fixed patterns")
    print("=" * 70)


if __name__ == "__main__":
    main()

"""
AI Flight Path Planning Module

Implements three path-planning algorithms used in autonomous drones:

  1. A*     — grid-based optimal path (fast, deterministic)
  2. RRT*   — sampling-based optimal path (handles complex 3D obstacles)
  3. Greedy — simple greedy waypoint follower (lowest complexity)

All planners operate on a 2-D occupancy grid for simplicity.
They can be extended to 3-D by adding an altitude axis.

Coordinate system
-----------------
  (row, col) grid indices  ←→  (north_m, east_m) local NED coordinates.
  Grid cell size is configurable (default 1 m).
"""

import math
import heapq
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

GridPos = Tuple[int, int]   # (row, col)
Path    = List[GridPos]


# ---------------------------------------------------------------------------
# Occupancy grid
# ---------------------------------------------------------------------------

class OccupancyGrid:
    """
    2-D grid where each cell is either FREE (0) or OCCUPIED (1).

    Provides helpers to convert between grid coords and metric NED coords.
    """

    FREE     = 0
    OCCUPIED = 1

    def __init__(self, rows: int, cols: int, cell_size_m: float = 1.0) -> None:
        self.rows = rows
        self.cols = cols
        self.cell_size_m = cell_size_m
        self._grid: List[List[int]] = [[self.FREE] * cols for _ in range(rows)]

    # ------------------------------------------------------------------
    # Grid operations
    # ------------------------------------------------------------------

    def set(self, row: int, col: int, value: int) -> None:
        if self._in_bounds(row, col):
            self._grid[row][col] = value

    def get(self, row: int, col: int) -> int:
        if self._in_bounds(row, col):
            return self._grid[row][col]
        return self.OCCUPIED  # treat out-of-bounds as obstacle

    def is_free(self, row: int, col: int) -> bool:
        return self.get(row, col) == self.FREE

    def add_obstacle_rect(self, r0: int, c0: int, r1: int, c1: int) -> None:
        """Mark a rectangular region as occupied."""
        for r in range(min(r0, r1), max(r0, r1) + 1):
            for c in range(min(c0, c1), max(c0, c1) + 1):
                self.set(r, c, self.OCCUPIED)

    def _in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols

    def neighbours(self, pos: GridPos,
                   allow_diagonal: bool = True) -> List[GridPos]:
        """Return passable neighbours of pos."""
        r, c = pos
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        if allow_diagonal:
            dirs += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        result = []
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if self._in_bounds(nr, nc) and self.is_free(nr, nc):
                result.append((nr, nc))
        return result

    # ------------------------------------------------------------------
    # Coordinate conversion
    # ------------------------------------------------------------------

    def to_metric(self, pos: GridPos) -> Tuple[float, float]:
        """Grid (row, col) → metric (north_m, east_m)."""
        r, c = pos
        return r * self.cell_size_m, c * self.cell_size_m

    def to_grid(self, north_m: float, east_m: float) -> GridPos:
        """Metric (north_m, east_m) → grid (row, col), clamped."""
        r = int(north_m / self.cell_size_m)
        c = int(east_m  / self.cell_size_m)
        return (max(0, min(self.rows - 1, r)),
                max(0, min(self.cols - 1, c)))

    def render(self, path: Optional[Path] = None,
               start: Optional[GridPos] = None,
               goal: Optional[GridPos] = None) -> str:
        """Return an ASCII visualisation of the grid."""
        path_set: Set[GridPos] = set(path) if path else set()
        lines = []
        for r in range(self.rows):
            row_chars = []
            for c in range(self.cols):
                pos = (r, c)
                if pos == start:
                    row_chars.append("S")
                elif pos == goal:
                    row_chars.append("G")
                elif pos in path_set:
                    row_chars.append("·")
                elif self._grid[r][c] == self.OCCUPIED:
                    row_chars.append("█")
                else:
                    row_chars.append(".")
            lines.append(" ".join(row_chars))
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# A* planner
# ---------------------------------------------------------------------------

def _euclidean(a: GridPos, b: GridPos) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def astar(grid: OccupancyGrid,
          start: GridPos,
          goal: GridPos) -> Optional[Path]:
    """
    A* path search on an OccupancyGrid.

    Returns the shortest path as a list of (row, col) tuples,
    or None if no path exists.
    """
    if not grid.is_free(*goal):
        return None

    # (f_cost, g_cost, position, parent)
    open_heap: List[Tuple[float, float, GridPos, Optional[GridPos]]] = []
    heapq.heappush(open_heap, (0.0, 0.0, start, None))

    came_from: Dict[GridPos, Optional[GridPos]] = {}
    g_score:   Dict[GridPos, float] = {start: 0.0}

    while open_heap:
        f, g, current, parent = heapq.heappop(open_heap)

        if current in came_from:
            continue
        came_from[current] = parent

        if current == goal:
            # Reconstruct path
            path: Path = []
            node: Optional[GridPos] = goal
            while node is not None:
                path.append(node)
                node = came_from[node]
            return list(reversed(path))

        for neighbour in grid.neighbours(current):
            step = _euclidean(current, neighbour)
            new_g = g + step
            if new_g < g_score.get(neighbour, math.inf):
                g_score[neighbour] = new_g
                h = _euclidean(neighbour, goal)
                heapq.heappush(open_heap,
                               (new_g + h, new_g, neighbour, current))

    return None   # no path found


# ---------------------------------------------------------------------------
# RRT* planner
# ---------------------------------------------------------------------------

@dataclass(order=True)
class RRTNode:
    """Node in the RRT* tree."""
    pos:    GridPos  = field(compare=False)
    parent: Optional["RRTNode"] = field(default=None, compare=False)
    cost:   float    = field(default=0.0)


def rrt_star(grid: OccupancyGrid,
             start: GridPos,
             goal: GridPos,
             max_iter: int = 2000,
             step_size: float = 3.0,
             goal_radius: float = 3.0,
             rewire_radius: float = 5.0,
             seed: Optional[int] = None) -> Optional[Path]:
    """
    RRT* (asymptotically optimal) path planner.

    Returns a path (list of grid positions) or None if not found within
    max_iter iterations.
    """
    rng = random.Random(seed)
    nodes: List[RRTNode] = [RRTNode(pos=start, cost=0.0)]

    def _nearest(sample: GridPos) -> RRTNode:
        return min(nodes, key=lambda n: _euclidean(n.pos, sample))

    def _steer(from_pos: GridPos, to_pos: GridPos) -> GridPos:
        d = _euclidean(from_pos, to_pos)
        if d <= step_size:
            return to_pos
        ratio = step_size / d
        r = int(from_pos[0] + ratio * (to_pos[0] - from_pos[0]))
        c = int(from_pos[1] + ratio * (to_pos[1] - from_pos[1]))
        return (max(0, min(grid.rows - 1, r)),
                max(0, min(grid.cols - 1, c)))

    def _collision_free(a: GridPos, b: GridPos) -> bool:
        steps = max(abs(b[0] - a[0]), abs(b[1] - a[1]), 1)
        for i in range(steps + 1):
            t = i / steps
            r = int(a[0] + t * (b[0] - a[0]))
            c = int(a[1] + t * (b[1] - a[1]))
            if not grid.is_free(r, c):
                return False
        return True

    best_goal_node: Optional[RRTNode] = None

    for _ in range(max_iter):
        # Sample (bias toward goal 10% of the time)
        if rng.random() < 0.10:
            sample = goal
        else:
            sample = (rng.randint(0, grid.rows - 1),
                      rng.randint(0, grid.cols - 1))

        nearest = _nearest(sample)
        new_pos = _steer(nearest.pos, sample)

        if not grid.is_free(*new_pos):
            continue
        if not _collision_free(nearest.pos, new_pos):
            continue

        # Find near nodes for rewiring
        near_nodes = [n for n in nodes
                      if _euclidean(n.pos, new_pos) <= rewire_radius]

        # Choose lowest-cost parent
        best_parent = nearest
        best_cost   = nearest.cost + _euclidean(nearest.pos, new_pos)
        for n in near_nodes:
            c = n.cost + _euclidean(n.pos, new_pos)
            if c < best_cost and _collision_free(n.pos, new_pos):
                best_parent = n
                best_cost   = c

        new_node = RRTNode(pos=new_pos, parent=best_parent, cost=best_cost)
        nodes.append(new_node)

        # Rewire
        for n in near_nodes:
            potential = new_node.cost + _euclidean(new_node.pos, n.pos)
            if potential < n.cost and _collision_free(new_node.pos, n.pos):
                n.parent = new_node
                n.cost   = potential

        # Check goal
        if _euclidean(new_pos, goal) <= goal_radius:
            if best_goal_node is None or new_node.cost < best_goal_node.cost:
                best_goal_node = new_node

    if best_goal_node is None:
        return None

    # Reconstruct path
    path: Path = []
    node: Optional[RRTNode] = best_goal_node
    while node is not None:
        path.append(node.pos)
        node = node.parent
    return list(reversed(path))


# ---------------------------------------------------------------------------
# Greedy waypoint follower (simplest, no obstacle avoidance)
# ---------------------------------------------------------------------------

def greedy_path(waypoints: List[GridPos]) -> Path:
    """Return the waypoints as-is (no replanning)."""
    return list(waypoints)


# ---------------------------------------------------------------------------
# Path smoother (optional post-processing)
# ---------------------------------------------------------------------------

def smooth_path(path: Path, grid: OccupancyGrid) -> Path:
    """
    String-pull (funnel) simplification: remove redundant waypoints
    where a direct line of sight exists.
    """
    if len(path) <= 2:
        return path

    smoothed: Path = [path[0]]
    i = 0
    while i < len(path) - 1:
        # Find the furthest visible point from path[i]
        j = len(path) - 1
        while j > i + 1:
            # Check line of sight using grid collision detection
            a, b = path[i], path[j]
            steps = max(abs(b[0] - a[0]), abs(b[1] - a[1]), 1)
            clear = True
            for k in range(steps + 1):
                t = k / steps
                r = int(a[0] + t * (b[0] - a[0]))
                c = int(a[1] + t * (b[1] - a[1]))
                if not grid.is_free(r, c):
                    clear = False
                    break
            if clear:
                break
            j -= 1
        smoothed.append(path[j])
        i = j

    return smoothed


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== AI Flight Path Planning Demo ===\n")

    # 20×20 grid with a wall obstacle
    g = OccupancyGrid(rows=20, cols=20)
    g.add_obstacle_rect(5, 5, 14, 7)   # vertical wall

    start = (0, 0)
    goal  = (18, 18)

    print("--- A* ---")
    path_a = astar(g, start, goal)
    if path_a:
        print(f"Path length: {len(path_a)} nodes")
        smoothed_a = smooth_path(path_a, g)
        print(f"Smoothed:    {len(smoothed_a)} nodes")
        print(g.render(smoothed_a, start, goal))
    else:
        print("No path found")

    print("\n--- RRT* ---")
    path_r = rrt_star(g, start, goal, max_iter=3000, seed=42)
    if path_r:
        print(f"Path length: {len(path_r)} nodes")
        print(g.render(path_r, start, goal))
    else:
        print("No path found within iteration limit")

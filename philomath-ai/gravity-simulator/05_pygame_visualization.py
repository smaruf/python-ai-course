"""
Pygame Visualization – Interactive Gravity Simulator
====================================================

This module brings the gravity simulator to life with a real-time pygame
window.  You can choose from four built-in scenarios and watch bodies
orbit, dance the figure-8, or tumble chaotically.

Controls:
    1 – 4        : Switch scenario  (1=figure-8, 2=Lagrange, 3=chaotic,
                                     4=Sun–Earth–Moon)
    SPACE        : Pause / resume simulation
    R            : Reset current scenario
    T            : Toggle body trails on / off
    +  / -       : Zoom in / out
    Arrow keys   : Pan the view
    S            : Slow down (halve the simulation speed)
    F            : Speed up  (double the simulation speed)
    ESC / Q      : Quit

Visual features:
    - Colour-coded bodies with unique RGB tones
    - Fading trail lines that fade out as they age
    - Body radius scaled to the log of mass for readability
    - On-screen HUD: scenario name, time, step count, energy
    - Centre-of-mass marker

Learning Objectives:
    - Build a real-time physics simulation loop with pygame
    - Map simulation coordinates to screen pixels (scaling + panning)
    - Draw anti-aliased lines for smooth trails
    - Handle keyboard events to control the simulation interactively

Video Reference:
    - Chapter 4 of "Programming for Lovers in Python"
    - https://programmingforlovers.com/chapters/chapter-4/
"""

import sys
import os
import math

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

from importlib.util import spec_from_file_location, module_from_spec as _mfs


def _load(name):
    path = os.path.join(_DIR, name)
    spec = spec_from_file_location(name[:-3], path)
    mod  = _mfs(spec)
    spec.loader.exec_module(mod)
    return mod


_vm    = _load("01_vector_math.py")
_body  = _load("02_body.py")
_gsim  = _load("03_gravity_simulation.py")
_3body = _load("04_three_body_problem.py")

Vector2D              = _vm.Vector2D
Body                  = _body.Body
leapfrog_step         = _gsim.leapfrog_step
leapfrog_step_dim     = _3body.leapfrog_step_dim
shift_to_com_frame    = _3body.shift_to_com_frame
centre_of_mass        = _3body.centre_of_mass
create_figure_eight   = _3body.create_figure_eight
create_lagrange_triangle   = _3body.create_lagrange_triangle
create_chaotic_three_body  = _3body.create_chaotic_three_body
create_sun_earth_moon      = _3body.create_sun_earth_moon

# ── Window / display settings ─────────────────────────────────────────────────

WINDOW_WIDTH  = 1000
WINDOW_HEIGHT = 700
WINDOW_TITLE  = "Gravity Simulator – Three-Body Problem"

BACKGROUND    = (10, 10, 20)          # deep space dark blue
HUD_COLOR     = (180, 180, 200)
TRAIL_ALPHA   = 180                   # maximum trail opacity
COM_COLOR     = (100, 100, 100)       # centre-of-mass marker

# ── Scenario definitions ──────────────────────────────────────────────────────

SCENARIOS = {
    1: {
        "name":        "Figure-8 (Chenciner & Montgomery, 2000)",
        "factory":     lambda: create_figure_eight(max_trail=600),
        "dt":          0.0005,
        "steps_per_frame": 5,
        "scale":       220,           # pixels per simulation unit
        "si_units":    False,
        "softening":   1e-4,
    },
    2: {
        "name":        "Lagrange Equilateral Triangle",
        "factory":     lambda: create_lagrange_triangle(max_trail=400),
        "dt":          0.001,
        "steps_per_frame": 3,
        "scale":       280,
        "si_units":    False,
        "softening":   1e-4,
    },
    3: {
        "name":        "Chaotic Three-Body System",
        "factory":     lambda: create_chaotic_three_body(max_trail=400),
        "dt":          0.005,
        "steps_per_frame": 2,
        "scale":       120,
        "si_units":    False,
        "softening":   1e-3,
    },
    4: {
        "name":        "Sun – Earth – Moon (SI units)",
        "factory":     lambda: create_sun_earth_moon(max_trail=400),
        "dt":          3600.0,        # 1 hour per step
        "steps_per_frame": 24,        # advance 24 h per frame
        "scale":       3e-9,          # pixels per metre
        "si_units":    True,
        "softening":   1e6,
    },
}

# ── Coordinate helpers ────────────────────────────────────────────────────────


def sim_to_screen(pos, scale, offset_x, offset_y):
    """
    Convert a simulation position (Vector2D) to pygame screen coordinates.

    Args:
        pos      (Vector2D): Position in simulation units
        scale    (float)   : Pixels per simulation unit
        offset_x (float)   : Horizontal pan offset in pixels
        offset_y (float)   : Vertical pan offset in pixels

    Returns:
        tuple (int, int): Pixel coordinates
    """
    sx = int(WINDOW_WIDTH  / 2 + pos.x * scale + offset_x)
    sy = int(WINDOW_HEIGHT / 2 - pos.y * scale + offset_y)
    return (sx, sy)


def body_radius(body, si_units):
    """
    Choose a display radius for a body based on its mass.

    SI scenario uses a logarithmic scale; dimensionless uses linear.

    Args:
        body     (Body): The body
        si_units (bool): True for SI unit scenario

    Returns:
        int: Radius in pixels (at least 4)
    """
    if si_units:
        # Map solar-mass scale to pixels
        sun_mass = 1.989e30
        ratio    = body.mass / sun_mass
        return max(4, int(6 + 6 * math.log10(ratio + 1e-5) + 30))
    else:
        return max(4, int(5 + body.mass * 3))


# ── Drawing helpers ───────────────────────────────────────────────────────────


def draw_trails(surface, bodies, scale, offset_x, offset_y):
    """
    Draw fading trail lines for each body.

    Older trail points are drawn with lower alpha (darker); the trail
    fades smoothly from opaque at the head to transparent at the tail.

    Args:
        surface          : pygame Surface
        bodies (list[Body]): Bodies whose trails to draw
        scale, offset_x, offset_y: coordinate mapping parameters
    """
    import pygame
    for body in bodies:
        trail = body.trail
        n = len(trail)
        if n < 2:
            continue
        for i in range(1, n):
            # Fade: tail is dark, head is bright
            alpha = int(TRAIL_ALPHA * i / n)
            r, g, b = body.color
            color = (int(r * alpha / 255),
                     int(g * alpha / 255),
                     int(b * alpha / 255))
            p1 = sim_to_screen(trail[i - 1], scale, offset_x, offset_y)
            p2 = sim_to_screen(trail[i],     scale, offset_x, offset_y)
            pygame.draw.line(surface, color, p1, p2, 1)


def draw_bodies(surface, bodies, scale, offset_x, offset_y, si_units):
    """
    Draw each body as a filled circle with an outline glow.

    Args:
        surface: pygame Surface
        bodies (list[Body]): Bodies to draw
        scale, offset_x, offset_y: coordinate mapping
        si_units (bool): Use SI mass-to-radius mapping
    """
    import pygame
    for body in bodies:
        pos = sim_to_screen(body.position, scale, offset_x, offset_y)
        r   = body_radius(body, si_units)
        # Glow halo
        glow_color = tuple(min(255, c + 60) for c in body.color)
        pygame.draw.circle(surface, glow_color, pos, r + 2)
        # Main body
        pygame.draw.circle(surface, body.color,  pos, r)


def draw_com(surface, bodies, scale, offset_x, offset_y):
    """Draw a small cross at the centre of mass."""
    import pygame
    com = centre_of_mass(bodies)
    sx, sy = sim_to_screen(com, scale, offset_x, offset_y)
    size = 6
    pygame.draw.line(surface, COM_COLOR, (sx - size, sy), (sx + size, sy), 1)
    pygame.draw.line(surface, COM_COLOR, (sx, sy - size), (sx, sy + size), 1)


def draw_hud(surface, font, scenario_name, step, time_val, paused,
             show_trails, si_units, dt, steps_per_frame, speed_mult):
    """
    Render the heads-up display text in the top-left corner.

    Args:
        surface: pygame Surface
        font: pygame Font
        scenario_name (str): Current scenario label
        step  (int): Current step count
        time_val (float): Elapsed simulation time
        paused (bool): Is the simulation paused?
        show_trails (bool): Are trails visible?
        si_units (bool): SI or dimensionless units?
        dt (float): Time step
        steps_per_frame (int): Current steps per frame
        speed_mult (float): Speed multiplier
    """
    import pygame
    time_str = (f"{time_val / 86400:.1f} days"
                if si_units else f"{time_val:.4f} tu")
    lines = [
        f"Scenario: {scenario_name}",
        f"Time: {time_str}   Step: {step:,}",
        f"dt={dt:.2e}  x{steps_per_frame} steps/frame  speed×{speed_mult:.1f}",
        f"{'[PAUSED]' if paused else '[RUNNING]'}  "
        f"Trails={'ON' if show_trails else 'OFF'}",
        "",
        "Keys: 1-4=scene  SPACE=pause  R=reset  T=trails",
        "      +/-=zoom   arrows=pan   S/F=speed  ESC=quit",
    ]
    y = 8
    for line in lines:
        surf = font.render(line, True, HUD_COLOR)
        surface.blit(surf, (8, y))
        y += 16


# ── Text-mode fallback (no pygame) ───────────────────────────────────────────


def _run_text_demo():
    """Run a short text-mode demo when pygame is unavailable."""
    print("\nGravity Simulator – text demo (no pygame)\n")

    print("=== Figure-8 scenario ===")
    bodies = create_figure_eight(max_trail=0)
    shift_to_com_frame(bodies)
    dt    = 0.001
    steps = 500
    for i in range(steps):
        leapfrog_step_dim(bodies, dt)

    for b in bodies:
        print(f"  {b.name}: pos=({b.position.x:.4f}, {b.position.y:.4f})")

    print("\n=== Chaotic scenario (10 steps) ===")
    chaos = create_chaotic_three_body()
    for step in range(10):
        leapfrog_step_dim(chaos, 0.01)
        if step % 3 == 0:
            com = centre_of_mass(chaos)
            print(f"  Step {step:3d} | CoM=({com.x:.4f}, {com.y:.4f})")

    print("\n✓ Text demo complete")


# ── Main pygame loop ──────────────────────────────────────────────────────────


def main():
    """
    Launch the interactive gravity simulator window.

    Falls back to a text-mode demo if pygame is not installed.
    """
    try:
        import pygame
    except ImportError:
        print("pygame is not installed. Run: pip install pygame")
        _run_text_demo()
        return

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    font   = pygame.font.SysFont("monospace", 13)
    clock  = pygame.time.Clock()

    # ── State ─────────────────────────────────────────────────────────────────
    scenario_id   = 1
    cfg           = SCENARIOS[scenario_id]
    bodies        = cfg["factory"]()
    if not cfg["si_units"]:
        shift_to_com_frame(bodies)

    dt              = cfg["dt"]
    steps_per_frame = cfg["steps_per_frame"]
    scale           = cfg["scale"]
    si_units        = cfg["si_units"]
    softening       = cfg["softening"]

    step            = 0
    sim_time        = 0.0
    paused          = False
    show_trails     = True
    offset_x        = 0.0
    offset_y        = 0.0
    speed_mult      = 1.0      # user-adjustable speed multiplier

    running = True
    while running:
        # ── Event handling ────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                k = event.key

                # Quit
                if k in (pygame.K_ESCAPE, pygame.K_q):
                    running = False

                # Scenario switch
                elif k in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    scenario_id     = int(pygame.key.name(k))
                    cfg             = SCENARIOS[scenario_id]
                    bodies          = cfg["factory"]()
                    if not cfg["si_units"]:
                        shift_to_com_frame(bodies)
                    dt              = cfg["dt"]
                    steps_per_frame = cfg["steps_per_frame"]
                    scale           = cfg["scale"]
                    si_units        = cfg["si_units"]
                    softening       = cfg["softening"]
                    step            = 0
                    sim_time        = 0.0
                    offset_x        = 0.0
                    offset_y        = 0.0
                    speed_mult      = 1.0

                # Pause / resume
                elif k == pygame.K_SPACE:
                    paused = not paused

                # Reset
                elif k == pygame.K_r:
                    bodies = cfg["factory"]()
                    if not cfg["si_units"]:
                        shift_to_com_frame(bodies)
                    step     = 0
                    sim_time = 0.0
                    offset_x = 0.0
                    offset_y = 0.0

                # Toggle trails
                elif k == pygame.K_t:
                    show_trails = not show_trails
                    if not show_trails:
                        for b in bodies:
                            b.clear_trail()

                # Zoom
                elif k == pygame.K_EQUALS or k == pygame.K_PLUS:
                    scale *= 1.25
                elif k == pygame.K_MINUS:
                    scale /= 1.25

                # Pan
                elif k == pygame.K_LEFT:
                    offset_x -= 40
                elif k == pygame.K_RIGHT:
                    offset_x += 40
                elif k == pygame.K_UP:
                    offset_y -= 40
                elif k == pygame.K_DOWN:
                    offset_y += 40

                # Speed
                elif k == pygame.K_s:
                    speed_mult = max(0.125, speed_mult / 2.0)
                    steps_per_frame = max(1, int(cfg["steps_per_frame"] * speed_mult))
                elif k == pygame.K_f:
                    speed_mult = min(32.0, speed_mult * 2.0)
                    steps_per_frame = max(1, int(cfg["steps_per_frame"] * speed_mult))

        # ── Advance simulation ────────────────────────────────────────────────
        if not paused:
            integrator = leapfrog_step_dim if not si_units else leapfrog_step
            for _ in range(steps_per_frame):
                if si_units:
                    leapfrog_step(bodies, dt, softening)
                else:
                    leapfrog_step_dim(bodies, dt, softening)
                sim_time += dt
                step     += 1

        # ── Draw ──────────────────────────────────────────────────────────────
        screen.fill(BACKGROUND)

        if show_trails:
            draw_trails(screen, bodies, scale, offset_x, offset_y)

        draw_com(screen, bodies, scale, offset_x, offset_y)
        draw_bodies(screen, bodies, scale, offset_x, offset_y, si_units)
        draw_hud(screen, font, cfg["name"], step, sim_time,
                 paused, show_trails, si_units, dt, steps_per_frame,
                 speed_mult)

        pygame.display.flip()
        clock.tick(60)   # cap at 60 fps

    pygame.quit()


if __name__ == "__main__":
    print("=" * 65)
    print("GRAVITY SIMULATOR – PYGAME VISUALIZATION")
    print("=" * 65)
    print("\nScenarios:")
    for sid, cfg in SCENARIOS.items():
        print(f"  [{sid}] {cfg['name']}")
    print("\nControls:")
    print("  1-4      Switch scenario")
    print("  SPACE    Pause / resume")
    print("  R        Reset current scenario")
    print("  T        Toggle trails")
    print("  + / -    Zoom in / out")
    print("  Arrows   Pan view")
    print("  S / F    Slow / fast")
    print("  ESC / Q  Quit")
    print("\nLaunching window...")
    main()

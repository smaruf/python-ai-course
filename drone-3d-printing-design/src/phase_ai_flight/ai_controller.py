"""
AI Drone Controller Module

Integrates:
  • Rule-based decision engine (battery / signal failsafe, geofence)
  • Neural-network stub for edge-AI object detection and avoidance
  • Velocity Obstacle (VO) collision avoidance
  • Boids swarm coordination
  • Proportional Navigation guidance (for study/context only)

All neural-network calls are stubs that can be replaced with real
TensorFlow Lite / ONNX inference when running on actual hardware.
"""

import math
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

Vec2 = Tuple[float, float]   # (x, y) in metres


def _v2_add(a: Vec2, b: Vec2) -> Vec2:
    return (a[0] + b[0], a[1] + b[1])


def _v2_sub(a: Vec2, b: Vec2) -> Vec2:
    return (a[0] - b[0], a[1] - b[1])


def _v2_scale(v: Vec2, s: float) -> Vec2:
    return (v[0] * s, v[1] * s)


def _v2_norm(v: Vec2) -> float:
    return math.sqrt(v[0] ** 2 + v[1] ** 2)


def _v2_normalise(v: Vec2) -> Vec2:
    n = _v2_norm(v)
    return (v[0] / n, v[1] / n) if n > 1e-9 else (0.0, 0.0)


# ---------------------------------------------------------------------------
# Rule-based decision engine
# ---------------------------------------------------------------------------

class DroneState(Enum):
    IDLE     = "IDLE"
    ARMING   = "ARMING"
    MISSION  = "MISSION"
    RTH      = "RTH"
    LAND     = "LAND"
    EMERGENCY = "EMERGENCY"


@dataclass
class DroneContext:
    """Runtime snapshot of the drone's environment and health."""
    battery_pct:   float = 100.0
    rc_signal:     bool  = True
    gps_fix:       bool  = True
    obstacle_close: bool = False   # obstacle within collision radius
    geofence_ok:   bool  = True
    mission_done:  bool  = False


class RuleEngine:
    """
    Priority-ordered rule evaluator.

    Rules are (condition_fn, resulting_state) pairs checked top-down.
    The first matching rule wins.
    """

    RULES: List[Tuple[Callable[[DroneContext], bool], DroneState]] = []

    def __init__(self) -> None:
        self.RULES = [
            # Critical failures first
            (lambda c: not c.gps_fix and not c.rc_signal,
             DroneState.LAND),
            (lambda c: c.battery_pct < 10,
             DroneState.LAND),
            (lambda c: not c.geofence_ok,
             DroneState.RTH),
            (lambda c: not c.rc_signal or c.battery_pct < 20,
             DroneState.RTH),
            (lambda c: c.obstacle_close,
             DroneState.RTH),       # could be HOVER/AVOID in real impl
            (lambda c: c.mission_done,
             DroneState.RTH),
            # Default: continue mission
            (lambda c: True,
             DroneState.MISSION),
        ]

    def evaluate(self, context: DroneContext) -> DroneState:
        for condition, state in self.RULES:
            if condition(context):
                return state
        return DroneState.MISSION


# ---------------------------------------------------------------------------
# Neural-network stub (edge-AI interface)
# ---------------------------------------------------------------------------

@dataclass
class DetectedObject:
    label:      str
    confidence: float   # 0.0–1.0
    bbox_xywh:  Tuple[float, float, float, float]  # pixels
    distance_m: float = 0.0  # populated by depth sensor fusion


class ObjectDetector:
    """
    Stub for a real TFLite / ONNX YOLO model running on-device.

    Replace `_run_inference` with actual model call:
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        output = interpreter.get_tensor(output_details[0]['index'])
    """

    def __init__(self, confidence_threshold: float = 0.5) -> None:
        self.threshold = confidence_threshold
        self._model_loaded = False

    def load_model(self, model_path: str) -> None:
        """Load TFLite model (stub — replace with real loader)."""
        self._model_loaded = True

    def detect(self, frame) -> List[DetectedObject]:
        """
        Run object detection on a camera frame.

        Returns a list of detected objects above the confidence threshold.
        In this stub, returns an empty list (no model loaded).
        """
        if not self._model_loaded:
            return []
        return self._run_inference(frame)

    def _run_inference(self, frame) -> List[DetectedObject]:  # pragma: no cover
        """Override with real TFLite/ONNX inference."""
        return []


# ---------------------------------------------------------------------------
# Velocity Obstacle (VO) collision avoidance
# ---------------------------------------------------------------------------

@dataclass
class Agent:
    """A moving agent (drone or obstacle) in 2-D space."""
    position: Vec2
    velocity: Vec2
    radius:   float = 2.0   # metres (collision radius)


def compute_desired_velocity(agent: Agent,
                             goal: Vec2,
                             max_speed: float = 5.0) -> Vec2:
    """Return the unit vector toward the goal, scaled to max_speed."""
    delta = _v2_sub(goal, agent.position)
    dist  = _v2_norm(delta)
    if dist < 0.01:
        return (0.0, 0.0)
    scale = min(max_speed, dist)
    return _v2_scale(_v2_normalise(delta), scale)


def velocity_obstacle_avoid(agent: Agent,
                            obstacles: List[Agent],
                            desired_vel: Vec2,
                            max_speed: float = 5.0,
                            time_horizon: float = 4.0) -> Vec2:
    """
    Simplified Velocity Obstacle avoidance.

    Returns a safe velocity close to `desired_vel` that avoids all
    obstacles within `time_horizon` seconds.

    This is a heuristic approximation: for each conflicting obstacle
    we deflect the desired velocity perpendicular to the collision cone.
    """
    safe_vel = desired_vel

    for obs in obstacles:
        rel_pos = _v2_sub(obs.position, agent.position)
        dist    = _v2_norm(rel_pos)
        combined_radius = agent.radius + obs.radius + 0.5  # safety margin

        if dist < combined_radius:
            # Already overlapping — move directly away
            away = _v2_scale(_v2_normalise(rel_pos), -max_speed)
            return away

        # Time-to-collision estimate
        rel_vel = _v2_sub(agent.velocity, obs.velocity)
        rel_speed = _v2_norm(rel_vel)

        if rel_speed < 1e-6:
            continue

        cos_theta = combined_radius / dist
        if abs(cos_theta) >= 1.0:
            continue

        # Check if desired velocity is inside VO cone
        dot = (desired_vel[0] * rel_pos[0] + desired_vel[1] * rel_pos[1])
        cross = (desired_vel[0] * rel_pos[1] - desired_vel[1] * rel_pos[0])

        if dot <= 0 or abs(cross) > dist * math.sqrt(1 - cos_theta ** 2) * max_speed:
            continue   # no conflict

        # Deflect perpendicular to rel_pos
        perp = (-rel_pos[1] / dist, rel_pos[0] / dist)
        safe_vel = _v2_scale(perp, max_speed)

    return safe_vel


# ---------------------------------------------------------------------------
# Boids swarm coordination
# ---------------------------------------------------------------------------

@dataclass
class BoidAgent:
    """A single boid in the swarm."""
    position: Vec2
    velocity: Vec2
    max_speed: float = 5.0
    id:        int   = 0


def boids_update(agents: List[BoidAgent],
                 sep_radius: float = 5.0,
                 align_radius: float = 15.0,
                 coh_radius: float   = 20.0,
                 sep_weight: float   = 1.5,
                 align_weight: float = 1.0,
                 coh_weight: float   = 1.0) -> List[BoidAgent]:
    """
    One iteration of the Boids algorithm (separation, alignment, cohesion).

    Returns updated agents with new velocities applied.
    """
    new_agents = []

    for agent in agents:
        sep   = [0.0, 0.0]
        align = [0.0, 0.0]
        coh   = [0.0, 0.0]
        n_sep = n_align = n_coh = 0

        for other in agents:
            if other.id == agent.id:
                continue
            d = _v2_norm(_v2_sub(other.position, agent.position))

            if d < sep_radius and d > 1e-6:
                diff = _v2_sub(agent.position, other.position)
                diff = _v2_scale(_v2_normalise(diff), 1.0 / d)
                sep[0] += diff[0]; sep[1] += diff[1]
                n_sep += 1

            if d < align_radius:
                align[0] += other.velocity[0]
                align[1] += other.velocity[1]
                n_align += 1

            if d < coh_radius:
                coh[0] += other.position[0]
                coh[1] += other.position[1]
                n_coh += 1

        steering = [agent.velocity[0], agent.velocity[1]]

        if n_sep:
            steering[0] += sep_weight   * sep[0] / n_sep
            steering[1] += sep_weight   * sep[1] / n_sep
        if n_align:
            avg_v = (align[0] / n_align, align[1] / n_align)
            steering[0] += align_weight * avg_v[0]
            steering[1] += align_weight * avg_v[1]
        if n_coh:
            centre = (coh[0] / n_coh, coh[1] / n_coh)
            toward = _v2_sub(centre, agent.position)
            n_toward = _v2_normalise(toward)
            steering[0] += coh_weight * n_toward[0]
            steering[1] += coh_weight * n_toward[1]

        # Clamp to max speed
        speed = _v2_norm((steering[0], steering[1]))
        if speed > agent.max_speed:
            steering[0] = steering[0] / speed * agent.max_speed
            steering[1] = steering[1] / speed * agent.max_speed

        new_vel = (steering[0], steering[1])
        new_pos = _v2_add(agent.position, new_vel)

        new_agents.append(BoidAgent(
            position=new_pos,
            velocity=new_vel,
            max_speed=agent.max_speed,
            id=agent.id,
        ))

    return new_agents


# ---------------------------------------------------------------------------
# Proportional Navigation guidance (study/context — see safety note)
# ---------------------------------------------------------------------------
# ⚠ SAFETY & LEGAL NOTE ⚠
# Proportional navigation (PN) is a classical missile guidance law used in
# academic and defence research.  The implementation below is provided
# **strictly for educational purposes** — understanding how guidance
# algorithms work.
#
# Deploying any impact-guidance system on an actual aircraft is:
#   • Illegal in most jurisdictions without appropriate licences
#   • Subject to ITAR/EAR export control regulations
#   • Dangerous to human life and property
#
# This code must NOT be used to guide real aircraft toward any target.
# ---------------------------------------------------------------------------

def proportional_navigation(
    pursuer_pos: Vec2,
    pursuer_vel: Vec2,
    target_pos:  Vec2,
    target_vel:  Vec2,
    nav_constant: float = 3.0,
) -> Vec2:
    """
    Pure Proportional Navigation guidance law (2-D, educational only).

    Returns the commanded lateral acceleration vector.

    Parameters
    ----------
    pursuer_pos, pursuer_vel : current position/velocity of the pursuer
    target_pos,  target_vel  : current position/velocity of the target
    nav_constant             : navigation gain N (typically 3–5)

    Notes
    -----
    a_cmd = N * V_c * omega
    where V_c is closing speed and omega is line-of-sight rotation rate.
    """
    # Line-of-sight vector
    los = _v2_sub(target_pos, pursuer_pos)
    los_dist = _v2_norm(los)

    if los_dist < 1e-6:
        return (0.0, 0.0)

    los_unit = _v2_normalise(los)

    # Relative velocity
    rel_vel = _v2_sub(target_vel, pursuer_vel)

    # Closing speed (positive = approaching)
    closing_speed = -(rel_vel[0] * los_unit[0] + rel_vel[1] * los_unit[1])

    # LOS rotation rate (cross product component)
    omega = (los_unit[0] * rel_vel[1] - los_unit[1] * rel_vel[0]) / los_dist

    # Commanded lateral acceleration (perpendicular to LOS)
    perp = (-los_unit[1], los_unit[0])
    a_mag = nav_constant * closing_speed * omega
    return _v2_scale(perp, a_mag)


# ---------------------------------------------------------------------------
# High-level AI controller
# ---------------------------------------------------------------------------

class AIController:
    """
    Combines rule engine, object detector, and VO avoidance into a
    single update loop.
    """

    def __init__(self) -> None:
        self.rule_engine = RuleEngine()
        self.detector    = ObjectDetector()
        self.state       = DroneState.IDLE

    def step(self,
             context:      DroneContext,
             agent:        Agent,
             goal:         Vec2,
             obstacles:    List[Agent],
             max_speed:    float = 5.0) -> Dict:
        """
        Single control step.

        Returns
        -------
        dict with keys: state, velocity, avoidance_active
        """
        # 1. Rule-based state decision
        self.state = self.rule_engine.evaluate(context)

        # 2. Compute desired velocity toward goal
        desired_vel = compute_desired_velocity(agent, goal, max_speed)

        # 3. Apply VO avoidance
        safe_vel = velocity_obstacle_avoid(agent, obstacles, desired_vel, max_speed)
        avoidance_active = safe_vel != desired_vel

        return {
            "state":            self.state.value,
            "velocity":         safe_vel,
            "avoidance_active": avoidance_active,
        }


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== AI Controller Demo ===\n")

    # --- Rule engine ---
    print("Rule engine decisions:")
    engine = RuleEngine()
    cases = [
        (DroneContext(battery_pct=80, rc_signal=True),  "normal"),
        (DroneContext(battery_pct=15, rc_signal=True),  "low battery"),
        (DroneContext(battery_pct=80, rc_signal=False), "RC lost"),
        (DroneContext(battery_pct=5,  rc_signal=False), "critical"),
    ]
    for ctx, desc in cases:
        decision = engine.evaluate(ctx)
        print(f"  {desc:20s}: {decision.value}")

    print()

    # --- VO avoidance ---
    print("Velocity obstacle avoidance:")
    me      = Agent(position=(0.0, 0.0),   velocity=(3.0, 0.0))
    blocker = Agent(position=(10.0, 0.0),  velocity=(-1.0, 0.0), radius=3.0)
    desired = compute_desired_velocity(me, (20.0, 0.0))
    safe    = velocity_obstacle_avoid(me, [blocker], desired)
    print(f"  Desired : ({desired[0]:.2f}, {desired[1]:.2f})")
    print(f"  Safe    : ({safe[0]:.2f}, {safe[1]:.2f})")
    print(f"  Avoidance triggered: {safe != desired}")

    print()

    # --- Boids swarm ---
    print("Boids swarm (5 agents, 3 steps):")
    rng    = random.Random(42)
    swarm  = [BoidAgent(position=(rng.uniform(0, 20), rng.uniform(0, 20)),
                        velocity=(rng.uniform(-2, 2), rng.uniform(-2, 2)),
                        id=i)
              for i in range(5)]
    for step in range(3):
        swarm = boids_update(swarm)
    for a in swarm:
        print(f"  Agent {a.id}: pos=({a.position[0]:.1f}, {a.position[1]:.1f})  "
              f"vel=({a.velocity[0]:.2f}, {a.velocity[1]:.2f})")

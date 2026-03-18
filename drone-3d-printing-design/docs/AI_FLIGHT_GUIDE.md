# AI Flight Guide — Autonomous Drone Systems

## Overview

AI autonomy transforms a drone from a remote-controlled vehicle into a self-directed agent capable of planning, perceiving, and reacting without human input. The stack layers three capabilities: **perception** (sensors + ML inference), **planning** (path finding + mission logic), and **control** (flight controller commands).

```
Mission Goal → Path Planner → Obstacle Avoidance → Waypoint Controller
                                                          │
                         Sensors ◄──────────────── Flight State
              (GPS · IMU · Lidar · Camera)
```

---

## 1. Flight Path Planning

### A* for Waypoint Navigation

A* searches a discrete grid minimising `f(n) = g(n) + h(n)` (cost-so-far + Euclidean heuristic).

```python
import heapq, math

def astar(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    open_set = [(0.0, start)]
    came_from, g = {}, {start: 0.0}
    while open_set:
        _, cur = heapq.heappop(open_set)
        if cur == goal:
            path = []
            while cur in came_from:
                path.append(cur); cur = came_from[cur]
            return [start] + path[::-1]
        r, c = cur
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            nb = (r+dr, c+dc)
            if 0 <= nb[0] < rows and 0 <= nb[1] < cols and grid[nb[0]][nb[1]] == 0:
                ng = g[cur] + math.hypot(dr, dc)
                if ng < g.get(nb, float('inf')):
                    came_from[nb] = cur; g[nb] = ng
                    heapq.heappush(open_set, (ng + math.hypot(nb[0]-goal[0], nb[1]-goal[1]), nb))
    return []
```

### RRT* for Obstacle-Rich Environments

RRT* grows a random-sampling tree in continuous space and rewires it toward an optimal path — useful for high-dimensional or irregular obstacle fields.

```python
import random

class Node:
    def __init__(self, x, y): self.x, self.y, self.parent, self.cost = x, y, None, 0.0

def rrt_star(start, goal, obstacles, max_iter=1000, step=1.0, goal_r=1.5):
    nodes = [Node(*start)]
    for _ in range(max_iter):
        rx, ry = goal if random.random() < 0.1 else (random.uniform(0,50), random.uniform(0,50))
        nearest = min(nodes, key=lambda n: math.hypot(n.x-rx, n.y-ry))
        theta = math.atan2(ry-nearest.y, rx-nearest.x)
        new = Node(nearest.x + step*math.cos(theta), nearest.y + step*math.sin(theta))
        if any(math.hypot(new.x-ox, new.y-oy) < r for ox, oy, r in obstacles): continue
        near = [n for n in nodes if math.hypot(n.x-new.x, n.y-new.y) < 3*step]
        best = min(near, key=lambda n: n.cost + math.hypot(n.x-new.x, n.y-new.y), default=nearest)
        new.parent, new.cost = best, best.cost + math.hypot(best.x-new.x, best.y-new.y)
        nodes.append(new)
        if math.hypot(new.x-goal[0], new.y-goal[1]) < goal_r:
            path, cur = [], new
            while cur: path.append((cur.x, cur.y)); cur = cur.parent
            return path[::-1]
    return []
```

### ML-Based Adaptive Path Optimisation

After logging flights a lightweight MLP can learn a cost function that accounts for wind and battery drain, refining waypoint order beyond a static heuristic.

```python
# Pseudocode: plug a trained cost-prediction model into A* as a learned heuristic
def ml_heuristic(a, b, wind, altitude, model):
    import numpy as np
    features = np.array([[b[0]-a[0], b[1]-a[1], wind[0], wind[1], altitude]])
    return float(model.predict(features))
```

---

## 2. GPS Navigation

### WGS84 & NED Conversion

```python
EARTH_R = 6_371_000.0

def latlon_to_ned(origin_lat, origin_lon, lat, lon):
    """Return (north_m, east_m) offset from origin for short-range missions."""
    north = math.radians(lat - origin_lat) * EARTH_R
    east  = math.radians(lon - origin_lon) * EARTH_R * math.cos(math.radians(origin_lat))
    return north, east

def distance_m(lat1, lon1, lat2, lon2):
    """Haversine distance in metres."""
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return EARTH_R * 2 * math.asin(math.sqrt(a))
```

**GPS accuracy:** standard GPS ≈ 2–5 m CEP; SBAS ≈ 0.5–2 m; RTK (base station + NTRIP) ≈ 1–3 cm — required for precision landing and photogrammetry.

### Geofencing

```python
def point_in_polygon(px, py, poly):
    inside, j = False, len(poly)-1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and px < (xj-xi)*(py-yi)/(yj-yi)+xi:
            inside = not inside
        j = i
    return inside

def enforce_geofence(lat, lon, fence_verts, orig_lat, orig_lon):
    n, e = latlon_to_ned(orig_lat, orig_lon, lat, lon)
    if not point_in_polygon(n, e, fence_verts):
        raise RuntimeError("Geofence breach — initiating RTH")
```

---

## 3. Return-to-Home (RTH)

```python
def check_rth(battery_pct, last_rc_time, now, signal_timeout=3.0):
    if battery_pct <= 5:  return "LAND_NOW"
    if battery_pct <= 15: return "RTH"
    if now - last_rc_time > signal_timeout: return "RTH"
    return "NORMAL"

def safe_rth_altitude(current_pos, home_pos, obstacle_map, clearance_m=10.0):
    max_h = max(
        (o['height'] for o in obstacle_map
         if _segment_near(current_pos, home_pos, o['position'], o['radius'])),
        default=0.0
    )
    return max_h + clearance_m

def autonomous_land(fc, descent_rate=0.3, ground_threshold=0.15):
    import time
    while True:
        alt = fc.rangefinder.distance
        if alt is not None and alt < ground_threshold:
            fc.mode = "DISARM"; break
        fc.channels.overrides['3'] = throttle_for_descent(fc, descent_rate)
        time.sleep(0.05)
```

---

## 4. Object Detection & Avoidance

### Sensor Fusion (Vision + Lidar + Sonar)

```python
class FusedObstacleMap:
    def __init__(self): self.voxels = {}        # (ix,iy,iz) → occupancy probability

    def _key(self, x, y, z, res=0.2): return (int(x/res), int(y/res), int(z/res))

    def update_lidar(self, point_cloud):
        for x, y, z in point_cloud:
            k = self._key(x, y, z)
            self.voxels[k] = min(1.0, self.voxels.get(k, 0.0) + 0.4)

    def is_occupied(self, x, y, z, threshold=0.6):
        return self.voxels.get(self._key(x, y, z), 0.0) >= threshold
```

### Velocity Obstacle Avoidance

```python
def vo_avoidance(pos, vel, obstacles, max_speed=10.0):
    """Return adjusted velocity that avoids all dynamic obstacles."""
    safe = [
        (max_speed*math.cos(math.radians(a)), max_speed*math.sin(math.radians(a)))
        for a in range(0, 360, 5)
        if not any(_in_vo(pos, (max_speed*math.cos(math.radians(a)),
                                max_speed*math.sin(math.radians(a))), o) for o in obstacles)
    ]
    return min(safe, key=lambda v: math.hypot(v[0]-vel[0], v[1]-vel[1])) if safe else (0.0, 0.0)

def _in_vo(pos, v, obs, lookahead=3.0):
    fx, fy = pos[0]+v[0]*lookahead, pos[1]+v[1]*lookahead
    return math.hypot(fx-obs['x'], fy-obs['y']) < 1.5 + obs.get('radius', 0.5)
```

### YOLO Integration Concept

```python
class YOLOAvoidance:
    def __init__(self, model_path, depth_estimator):
        self.model = load_onnx_model(model_path)   # YOLOv8-nano ONNX
        self.depth = depth_estimator

    def detect_obstacles(self, frame):
        return [
            {'x': (b['x1']+b['x2'])/2, 'y': (b['y1']+b['y2'])/2,
             'distance': self.depth.estimate((b['x1']+b['x2'])/2, (b['y1']+b['y2'])/2),
             'radius': 1.0}
            for b in self.model.infer(frame) if b['conf'] > 0.5
        ]
```

---

## 5. Autonomous Mission Types

### Survey / Mapping

```python
def survey_grid(bounds, altitude_m, fov_deg=84, overlap=0.75):
    """Lawnmower waypoints from bounding box (min_lat, min_lon, max_lat, max_lon)."""
    spacing = 2 * altitude_m * math.tan(math.radians(fov_deg/2)) * (1 - overlap)
    min_lat, min_lon, max_lat, max_lon = bounds
    n_lines = int(distance_m(min_lat, min_lon, max_lat, min_lon) / spacing) + 1
    wps, direction = [], 1
    for i in range(n_lines):
        lat = min_lat + math.degrees(i * spacing / EARTH_R)
        row = [(lat, min_lon, altitude_m), (lat, max_lon, altitude_m)]
        wps.extend(row if direction == 1 else row[::-1])
        direction *= -1
    return wps
```

### Precision Package Delivery (Visual Landing)

```python
def visual_precision_land(fc, detector, descent_rate=0.2):
    import time
    while fc.location.global_relative_frame.alt > 0.3:
        tag = detector.detect()
        if tag:
            scale = fc.location.global_relative_frame.alt / detector.focal_length
            fc.send_ned_velocity(-tag.offset_y*scale*0.5, tag.offset_x*scale*0.5, descent_rate)
        time.sleep(0.1)
    fc.mode = "LAND"
```

### Swarm Coordination — Boids Algorithm

```python
def boids_velocity(agent, neighbours, w_sep=1.0, w_ali=1.5, w_coh=1.0):
    sep = [0.0, 0.0]; ali = [0.0, 0.0]; coh = [0.0, 0.0]
    for n in neighbours:
        dx, dy = agent['x']-n['x'], agent['y']-n['y']
        d = math.hypot(dx, dy) or 1e-9
        sep[0] += dx/d**2;  sep[1] += dy/d**2
        ali[0] += n['vx'];  ali[1] += n['vy']
        coh[0] += n['x'];   coh[1] += n['y']
    if neighbours:
        nc = len(neighbours)
        coh = [coh[0]/nc - agent['x'], coh[1]/nc - agent['y']]
    return [w_sep*sep[i] + w_ali*ali[i] + w_coh*coh[i] for i in range(2)]
```

---

## 6. Kamikaze / Impact Drone Pattern

> **⚠️ SAFETY & LEGAL NOTE — FOR ACADEMIC STUDY ONLY**
> Designing, building, or operating a drone with intent to damage property or harm
> persons is **illegal** in virtually every jurisdiction and constitutes a criminal
> offence under aviation, weapons, and terrorism statutes. Researchers working on
> legitimate counter-UAS or defence R&D must operate under institutional
> authorisation and applicable law. **Nothing in this section should be construed as
> instructions for construction or deployment.**

### Proportional Navigation Guidance (Conceptual)

Proportional Navigation (PN) is a classical intercept law from aerospace guidance theory. The commanded lateral acceleration is proportional to the line-of-sight rotation rate.

```python
# ACADEMIC / CONCEPTUAL ONLY
def proportional_navigation(pursuer_pos, target_pos, target_vel, pursuer_speed, N=3.0):
    """N: navigation constant (typically 3–5). Returns commanded lateral accel (m/s²)."""
    rel = [target_pos[i] - pursuer_pos[i] for i in range(2)]
    r   = math.hypot(*rel) or 1e-9
    # LOS rate from target velocity component perpendicular to LOS
    los_rate = (target_vel[0]*(-rel[1]) + target_vel[1]*rel[0]) / r**2
    return N * pursuer_speed * los_rate
```

### Legal & Ethical Summary

| Consideration | Detail |
|---------------|--------|
| Airspace law | Weaponised UAS prohibited outside military authorisation |
| Criminal liability | Civilian deployment is terrorism / attempted murder |
| Export controls | PN guidance code may fall under ITAR / EAR (US) |
| Counter-UAS research | Requires ethics board + MoD/DoD oversight |

---

## 7. AI Model Integration

### TensorFlow Lite on Edge Devices

```python
import tflite_runtime.interpreter as tflite
import numpy as np, cv2

class TFLiteDetector:
    def __init__(self, model_path):
        self.interp = tflite.Interpreter(model_path=model_path)
        self.interp.allocate_tensors()
        self.inp = self.interp.get_input_details()
        self.out = self.interp.get_output_details()

    def infer(self, image: np.ndarray):
        h, w = self.inp[0]['shape'][1:3]
        tensor = np.expand_dims(cv2.resize(image,(w,h)), 0).astype(np.float32) / 255.0
        self.interp.set_tensor(self.inp[0]['index'], tensor)
        self.interp.invoke()
        return self.interp.get_tensor(self.out[0]['index'])
```

**Recommended hardware:** Raspberry Pi 5 + Google Coral TPU, NVIDIA Jetson Nano/Orin.

### ONNX Deployment

```python
import onnxruntime as ort, numpy as np

class ONNXModel:
    def __init__(self, model_path):
        self.sess = ort.InferenceSession(model_path,
            providers=['CUDAExecutionProvider','CPUExecutionProvider'])
        self.input_name = self.sess.get_inputs()[0].name

    def run(self, frame: np.ndarray):
        return self.sess.run(None, {self.input_name: frame[np.newaxis].astype(np.float32)/255.0})
```

### ROS2 Integration

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix, LaserScan
from geometry_msgs.msg import TwistStamped

class AIFlightNode(Node):
    def __init__(self):
        super().__init__('ai_flight_node')
        self.create_subscription(NavSatFix,  '/gps/fix',    self._gps_cb,   10)
        self.create_subscription(LaserScan,  '/lidar/scan', self._lidar_cb, 10)
        self.vel_pub = self.create_publisher(TwistStamped,  '/cmd_vel',     10)

    def _gps_cb(self, msg: NavSatFix):
        self.get_logger().info(f'GPS: {msg.latitude:.6f}, {msg.longitude:.6f}')

    def _lidar_cb(self, msg: LaserScan):
        points = [
            (msg.ranges[i]*math.cos(msg.angle_min + i*msg.angle_increment),
             msg.ranges[i]*math.sin(msg.angle_min + i*msg.angle_increment), 0.0)
            for i in range(len(msg.ranges)) if msg.ranges[i] < msg.range_max
        ]
        self.obstacle_map.update_lidar(points)

def main():
    rclpy.init(); rclpy.spin(AIFlightNode()); rclpy.shutdown()
```

---

## 8. Testing AI Autonomy

### SITL (Software In The Loop)

```bash
# ArduPilot SITL — emulates flight controller in software
sim_vehicle.py -v ArduCopter --console --map

# Connect from Python (DroneKit)
from dronekit import connect
vehicle = connect('tcp:127.0.0.1:5762', wait_ready=True)
print(vehicle.location.global_frame)

# PX4 + Gazebo
make px4_sitl gazebo-classic_iris
ros2 launch px4_ros_com sensor_combined_listener.launch.py
```

### Unit Tests

```python
import unittest

class TestFlightAI(unittest.TestCase):
    def test_astar_finds_path(self):
        grid = [[0]*10 for _ in range(10)]
        grid[5] = [0,0,0,0,1,1,1,0,0,0]
        path = astar(grid, (0,0), (9,9))
        self.assertTrue(len(path) > 0)
        self.assertEqual(path[0], (0,0)); self.assertEqual(path[-1], (9,9))

    def test_geofence_breach(self):
        fence = [(0,0),(100,0),(100,100),(0,100)]
        with self.assertRaises(RuntimeError):
            enforce_geofence(200.0, 200.0, fence, 0.0, 0.0)

if __name__ == '__main__': unittest.main()
```

### Testing Checklist

| Stage | Tool | What to verify |
|-------|------|----------------|
| Unit | `pytest` | Path planner, GPS maths, geofence logic |
| Integration | SITL + DroneKit | RTH trigger, mission upload, waypoint sequencing |
| Simulation | Gazebo + PX4 | Sensor fusion, obstacle avoidance, visual landing |
| Hardware-in-loop | HITL bench | Timing, ESC response under AI commands |
| Field | Real aircraft, authorised airspace | End-to-end mission, edge-case recovery |

---

## Further Reading

- ArduPilot Developer Docs: <https://ardupilot.org/dev/>
- PX4 Developer Guide: <https://docs.px4.io/main/en/>
- ROS2 (Humble): <https://docs.ros.org/en/humble/>
- ICAO Annex 2 — Rules of the Air
- *Principles of Guided Flight*, Blakelock J. H. (classical guidance theory)

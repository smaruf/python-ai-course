"""
Graph-based waste collection route optimizer using Dijkstra's algorithm.
"""
from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Optional


@dataclass
class CollectionPoint:
    """Represents a waste collection point (bin/container)."""
    node_id: str
    location: str
    capacity_kg: float
    current_fill_kg: float
    waste_type: str = "ORGANIC"
    lat: float = 0.0
    lon: float = 0.0

    @property
    def fill_level(self) -> float:
        """Fill level as fraction 0–1."""
        return self.current_fill_kg / max(self.capacity_kg, 1e-6)

    @property
    def needs_collection(self) -> bool:
        return self.fill_level >= 0.8


@dataclass(order=True)
class _HeapEntry:
    cost: float
    node: str = field(compare=False)


class RouteOptimizer:
    """
    Graph-based collection route optimizer.
    Uses Dijkstra's algorithm; edge weights = distance + carbon penalty.
    """

    def __init__(self) -> None:
        self._nodes: dict[str, CollectionPoint] = {}
        # Adjacency: node_id -> list[(neighbour_id, distance_km)]
        self._edges: dict[str, list[tuple[str, float]]] = {}
        self._carbon_per_km = 0.21  # kg CO2 per km (diesel truck)

    def add_node(self, point: CollectionPoint) -> None:
        self._nodes[point.node_id] = point
        if point.node_id not in self._edges:
            self._edges[point.node_id] = []

    def add_edge(self, from_id: str, to_id: str, distance_km: float) -> None:
        self._edges.setdefault(from_id, []).append((to_id, distance_km))
        self._edges.setdefault(to_id, []).append((from_id, distance_km))

    def _edge_weight(self, distance_km: float, fill_level: float) -> float:
        """
        Combined edge weight: distance + urgency discount.
        Higher fill level → lower effective weight (prioritise fuller bins).
        """
        urgency_discount = 1.0 - 0.3 * fill_level
        return distance_km * urgency_discount

    def find_shortest_path(
        self, start: str, end: str
    ) -> tuple[list[str], float]:
        """
        Dijkstra shortest path from start to end.
        Returns (path, total_cost).
        """
        if start not in self._nodes or end not in self._nodes:
            return [], float("inf")

        dist: dict[str, float] = {nid: float("inf") for nid in self._nodes}
        dist[start] = 0.0
        prev: dict[str, Optional[str]] = {nid: None for nid in self._nodes}
        heap: list[_HeapEntry] = [_HeapEntry(0.0, start)]

        while heap:
            entry = heapq.heappop(heap)
            if entry.cost > dist[entry.node]:
                continue
            for neighbour, distance in self._edges.get(entry.node, []):
                fill = self._nodes[neighbour].fill_level if neighbour in self._nodes else 0.0
                w = self._edge_weight(distance, fill)
                new_cost = dist[entry.node] + w
                if new_cost < dist[neighbour]:
                    dist[neighbour] = new_cost
                    prev[neighbour] = entry.node
                    heapq.heappush(heap, _HeapEntry(new_cost, neighbour))

        if dist[end] == float("inf"):
            return [], float("inf")

        # Reconstruct path
        path: list[str] = []
        current: Optional[str] = end
        while current is not None:
            path.append(current)
            current = prev[current]
        return list(reversed(path)), dist[end]

    def plan_collection_route(
        self, depot: str, max_load_kg: float = 5000.0
    ) -> dict[str, Any]:
        """
        Plan a complete collection route starting and ending at depot.
        Visits all collection points that need collection.
        Uses nearest-neighbour heuristic.
        """
        to_visit = [
            nid for nid, pt in self._nodes.items()
            if pt.needs_collection and nid != depot
        ]

        if not to_visit:
            return {"route": [depot], "total_distance_km": 0.0,
                    "total_carbon_kg": 0.0, "collected_kg": 0.0}

        route = [depot]
        current = depot
        total_distance = 0.0
        collected_kg = 0.0
        current_load = 0.0
        remaining = set(to_visit)

        while remaining:
            # Find nearest unvisited node from current
            best_next: Optional[str] = None
            best_cost = float("inf")
            for candidate in remaining:
                _, cost = self.find_shortest_path(current, candidate)
                if cost < best_cost:
                    best_cost = cost
                    best_next = candidate

            if best_next is None:
                break

            point = self._nodes[best_next]
            if current_load + point.current_fill_kg > max_load_kg:
                # Return to depot to unload
                _, return_cost = self.find_shortest_path(current, depot)
                total_distance += return_cost
                route.append(depot)
                current = depot
                current_load = 0.0

            _, path_cost = self.find_shortest_path(current, best_next)
            total_distance += path_cost
            current_load += point.current_fill_kg
            collected_kg += point.current_fill_kg
            route.append(best_next)
            current = best_next
            remaining.discard(best_next)

        # Return to depot
        _, return_cost = self.find_shortest_path(current, depot)
        total_distance += return_cost
        route.append(depot)

        return {
            "route": route,
            "total_distance_km": round(total_distance, 2),
            "total_carbon_kg": round(total_distance * self._carbon_per_km, 3),
            "collected_kg": round(collected_kg, 1),
            "stops": len(to_visit),
        }


class CollectionScheduler:
    """Plans collection schedules based on fill rates and capacity."""

    def __init__(self, optimizer: RouteOptimizer) -> None:
        self._optimizer = optimizer
        self._fill_rates: dict[str, float] = {}  # kg/hour per node

    def set_fill_rate(self, node_id: str, kg_per_hour: float) -> None:
        self._fill_rates[node_id] = kg_per_hour

    def estimate_time_to_full(self, node_id: str) -> Optional[float]:
        """Return hours until node reaches capacity."""
        node = self._optimizer._nodes.get(node_id)
        if node is None:
            return None
        rate = self._fill_rates.get(node_id, 0.1)
        remaining_capacity = node.capacity_kg - node.current_fill_kg
        if rate <= 0:
            return None
        return remaining_capacity / rate

    def generate_schedule(
        self, depot: str, planning_horizon_hours: float = 24.0
    ) -> list[dict[str, Any]]:
        """
        Generate a collection schedule for the planning horizon.
        Returns list of {time, route_plan} events.
        """
        schedule: list[dict[str, Any]] = []
        check_time = 0.0
        check_interval = 4.0  # hours

        while check_time <= planning_horizon_hours:
            # Simulate fill levels
            for node_id, node in self._optimizer._nodes.items():
                rate = self._fill_rates.get(node_id, 0.0)
                node.current_fill_kg = min(
                    node.capacity_kg,
                    node.current_fill_kg + rate * check_interval
                )

            route_plan = self._optimizer.plan_collection_route(depot)
            if route_plan["collected_kg"] > 0:
                schedule.append({
                    "time_hours": check_time,
                    "datetime": (datetime.now() + timedelta(hours=check_time)).isoformat(),
                    "route_plan": route_plan,
                })
                # Reset collected nodes
                for node_id in self._optimizer._nodes:
                    if node_id != depot:
                        self._optimizer._nodes[node_id].current_fill_kg *= 0.05

            check_time += check_interval

        return schedule


class CarbonFootprintCalculator:
    """Calculate and track carbon footprints for waste operations."""

    TRANSPORT_FACTORS = {
        "diesel_truck": 0.210,   # kg CO2/km
        "electric_truck": 0.050,
        "cng_truck": 0.150,
    }

    TREATMENT_FACTORS = {
        "landfill": 0.60,
        "incineration": 1.20,
        "composting": 0.05,
        "anaerobic_digestion": -0.30,
        "recycling": -0.20,
    }

    def __init__(self, vehicle_type: str = "diesel_truck") -> None:
        self._vehicle_type = vehicle_type
        self._transport_factor = self.TRANSPORT_FACTORS.get(vehicle_type, 0.21)
        self._total_co2 = 0.0
        self._history: list[dict[str, Any]] = []

    def calculate_transport(self, distance_km: float) -> float:
        co2 = self._transport_factor * distance_km
        self._total_co2 += co2
        self._history.append({"type": "transport", "distance_km": distance_km, "co2_kg": co2})
        return co2

    def calculate_treatment(self, treatment: str, mass_kg: float) -> float:
        factor = self.TREATMENT_FACTORS.get(treatment, 0.5)
        co2 = factor * mass_kg
        self._total_co2 += co2
        self._history.append({"type": "treatment", "treatment": treatment,
                               "mass_kg": mass_kg, "co2_kg": co2})
        return co2

    def total_footprint(self) -> float:
        return round(self._total_co2, 4)

    def get_report(self) -> str:
        lines = ["=== Carbon Footprint Report ==="]
        for entry in self._history[-10:]:
            if entry["type"] == "transport":
                lines.append(f"  Transport {entry['distance_km']:.1f} km → {entry['co2_kg']:.3f} kg CO₂")
            else:
                lines.append(f"  Treatment ({entry['treatment']}) {entry['mass_kg']:.1f} kg → {entry['co2_kg']:.3f} kg CO₂")
        lines.append(f"TOTAL: {self.total_footprint():.3f} kg CO₂")
        return "\n".join(lines)

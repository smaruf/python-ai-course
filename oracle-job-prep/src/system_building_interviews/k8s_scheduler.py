"""
Kubernetes Scheduler Implementation

Tests: Resource allocation logic, scheduling algorithms, constraint satisfaction

A simplified Kubernetes scheduler demonstrating:
- Pod scheduling based on resource requirements
- Node selection algorithms
- Resource tracking and allocation
- Scheduling constraints (affinity, taints, tolerations)
"""

from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import threading


class PodStatus(Enum):
    """Pod status enumeration."""
    PENDING = "Pending"
    SCHEDULED = "Scheduled"
    RUNNING = "Running"
    FAILED = "Failed"


@dataclass
class Resources:
    """Resource requirements/capacity."""
    cpu_millicores: int  # CPU in millicores (1000 = 1 core)
    memory_mb: int  # Memory in MB
    
    def __add__(self, other: 'Resources') -> 'Resources':
        """Add two resource objects."""
        return Resources(
            cpu_millicores=self.cpu_millicores + other.cpu_millicores,
            memory_mb=self.memory_mb + other.memory_mb
        )
    
    def __sub__(self, other: 'Resources') -> 'Resources':
        """Subtract two resource objects."""
        return Resources(
            cpu_millicores=self.cpu_millicores - other.cpu_millicores,
            memory_mb=self.memory_mb - other.memory_mb
        )
    
    def fits_in(self, other: 'Resources') -> bool:
        """Check if this resource fits in another."""
        return (
            self.cpu_millicores <= other.cpu_millicores and
            self.memory_mb <= other.memory_mb
        )


@dataclass
class Pod:
    """Represents a Kubernetes Pod."""
    name: str
    namespace: str
    resource_requests: Resources
    resource_limits: Resources
    node_selector: Dict[str, str] = field(default_factory=dict)
    affinity: List[str] = field(default_factory=list)
    tolerations: Set[str] = field(default_factory=set)
    status: PodStatus = PodStatus.PENDING
    assigned_node: Optional[str] = None
    
    def __post_init__(self):
        """Validate pod configuration."""
        if not self.resource_requests.fits_in(self.resource_limits):
            raise ValueError("Resource requests exceed limits")


@dataclass
class Node:
    """Represents a Kubernetes Node."""
    name: str
    total_resources: Resources
    labels: Dict[str, str] = field(default_factory=dict)
    taints: Set[str] = field(default_factory=set)
    allocated_resources: Resources = field(default_factory=lambda: Resources(0, 0))
    pods: List[str] = field(default_factory=list)
    
    def available_resources(self) -> Resources:
        """Get available resources on the node."""
        return self.total_resources - self.allocated_resources
    
    def can_fit(self, pod: Pod) -> bool:
        """Check if pod can fit on this node."""
        return pod.resource_requests.fits_in(self.available_resources())
    
    def matches_selector(self, selector: Dict[str, str]) -> bool:
        """Check if node matches pod's node selector."""
        if not selector:
            return True
        return all(
            self.labels.get(key) == value
            for key, value in selector.items()
        )
    
    def tolerates_taints(self, tolerations: Set[str]) -> bool:
        """Check if pod tolerates all node taints."""
        return self.taints.issubset(tolerations)


class KubernetesScheduler:
    """
    Simplified Kubernetes scheduler.
    
    Features:
    - Resource-based scheduling
    - Node selection algorithms
    - Constraint satisfaction (labels, taints/tolerations)
    - Fair scheduling
    - Preemption (simplified)
    """
    
    def __init__(self):
        """Initialize scheduler."""
        self.nodes: Dict[str, Node] = {}
        self.pods: Dict[str, Pod] = {}
        self.pending_pods: List[str] = []
        self.lock = threading.Lock()
    
    def add_node(self, node: Node):
        """
        Add a node to the cluster.
        
        Args:
            node: Node to add
        """
        with self.lock:
            self.nodes[node.name] = node
    
    def remove_node(self, node_name: str) -> bool:
        """
        Remove a node from the cluster.
        
        Args:
            node_name: Name of node to remove
            
        Returns:
            True if node was removed
        """
        with self.lock:
            if node_name in self.nodes:
                del self.nodes[node_name]
                return True
            return False
    
    def submit_pod(self, pod: Pod):
        """
        Submit a pod for scheduling.
        
        Args:
            pod: Pod to schedule
        """
        with self.lock:
            self.pods[pod.name] = pod
            self.pending_pods.append(pod.name)
    
    def schedule_pending_pods(self) -> List[str]:
        """
        Schedule all pending pods.
        
        Returns:
            List of scheduled pod names
        """
        scheduled = []
        
        with self.lock:
            unscheduled = []
            
            for pod_name in self.pending_pods:
                pod = self.pods[pod_name]
                
                # Try to schedule the pod
                node = self._select_node(pod)
                
                if node:
                    # Allocate pod to node
                    self._allocate_pod(pod, node)
                    scheduled.append(pod_name)
                else:
                    # Cannot schedule yet
                    unscheduled.append(pod_name)
            
            self.pending_pods = unscheduled
        
        return scheduled
    
    def _select_node(self, pod: Pod) -> Optional[Node]:
        """
        Select the best node for a pod.
        
        Uses a scoring algorithm:
        1. Filter nodes that can fit the pod
        2. Filter by node selector
        3. Filter by taints/tolerations
        4. Score remaining nodes
        5. Select highest scoring node
        
        Args:
            pod: Pod to schedule
            
        Returns:
            Selected Node or None if no suitable node
        """
        candidates = []
        
        # Filter phase
        for node in self.nodes.values():
            # Check resource fit
            if not node.can_fit(pod):
                continue
            
            # Check node selector
            if not node.matches_selector(pod.node_selector):
                continue
            
            # Check taints/tolerations
            if not node.tolerates_taints(pod.tolerations):
                continue
            
            candidates.append(node)
        
        if not candidates:
            return None
        
        # Scoring phase
        best_node = None
        best_score = -1
        
        for node in candidates:
            score = self._score_node(node, pod)
            if score > best_score:
                best_score = score
                best_node = node
        
        return best_node
    
    def _score_node(self, node: Node, pod: Pod) -> float:
        """
        Score a node for a pod.
        
        Higher score = better fit
        
        Args:
            node: Node to score
            pod: Pod being scheduled
            
        Returns:
            Score (0-100)
        """
        score = 0.0
        
        # Prefer nodes with more available resources (load balancing)
        available = node.available_resources()
        total = node.total_resources
        
        cpu_utilization = (total.cpu_millicores - available.cpu_millicores) / total.cpu_millicores
        mem_utilization = (total.memory_mb - available.memory_mb) / total.memory_mb
        
        # Prefer less utilized nodes (0-50 points)
        score += (1 - cpu_utilization) * 25
        score += (1 - mem_utilization) * 25
        
        # Affinity bonus (0-30 points)
        if pod.affinity:
            for affinity in pod.affinity:
                if affinity in node.labels.values():
                    score += 30 / len(pod.affinity)
        
        # Fewer pods bonus (0-20 points)
        max_pods = 100
        pod_density = len(node.pods) / max_pods
        score += (1 - pod_density) * 20
        
        return score
    
    def _allocate_pod(self, pod: Pod, node: Node):
        """
        Allocate a pod to a node.
        
        Args:
            pod: Pod to allocate
            node: Node to allocate to
        """
        # Update node
        node.allocated_resources = node.allocated_resources + pod.resource_requests
        node.pods.append(pod.name)
        
        # Update pod
        pod.status = PodStatus.SCHEDULED
        pod.assigned_node = node.name
    
    def evict_pod(self, pod_name: str) -> bool:
        """
        Evict a pod from its node.
        
        Args:
            pod_name: Name of pod to evict
            
        Returns:
            True if pod was evicted
        """
        with self.lock:
            if pod_name not in self.pods:
                return False
            
            pod = self.pods[pod_name]
            
            if pod.assigned_node:
                node = self.nodes.get(pod.assigned_node)
                if node:
                    # Deallocate resources
                    node.allocated_resources = node.allocated_resources - pod.resource_requests
                    node.pods.remove(pod_name)
                    
                    # Update pod
                    pod.status = PodStatus.PENDING
                    pod.assigned_node = None
                    self.pending_pods.append(pod_name)
                    
                    return True
        
        return False
    
    def get_node_status(self) -> List[Dict]:
        """Get status of all nodes."""
        with self.lock:
            return [
                {
                    'name': node.name,
                    'total_cpu': node.total_resources.cpu_millicores,
                    'total_memory': node.total_resources.memory_mb,
                    'available_cpu': node.available_resources().cpu_millicores,
                    'available_memory': node.available_resources().memory_mb,
                    'pod_count': len(node.pods)
                }
                for node in self.nodes.values()
            ]


if __name__ == "__main__":
    print("Kubernetes Scheduler Example")
    print("=" * 60)
    
    # Create scheduler
    scheduler = KubernetesScheduler()
    
    # Add nodes
    print("\nAdding nodes to cluster...")
    scheduler.add_node(Node(
        name="node-1",
        total_resources=Resources(cpu_millicores=4000, memory_mb=8192),
        labels={"zone": "us-west", "type": "compute"}
    ))
    scheduler.add_node(Node(
        name="node-2",
        total_resources=Resources(cpu_millicores=8000, memory_mb=16384),
        labels={"zone": "us-east", "type": "memory"}
    ))
    scheduler.add_node(Node(
        name="node-3",
        total_resources=Resources(cpu_millicores=2000, memory_mb=4096),
        labels={"zone": "us-west", "type": "compute"}
    ))
    
    # Submit pods
    print("\nSubmitting pods for scheduling...")
    scheduler.submit_pod(Pod(
        name="web-server-1",
        namespace="default",
        resource_requests=Resources(cpu_millicores=500, memory_mb=1024),
        resource_limits=Resources(cpu_millicores=1000, memory_mb=2048),
        node_selector={"type": "compute"}
    ))
    scheduler.submit_pod(Pod(
        name="database-1",
        namespace="default",
        resource_requests=Resources(cpu_millicores=2000, memory_mb=4096),
        resource_limits=Resources(cpu_millicores=4000, memory_mb=8192),
        node_selector={"type": "memory"}
    ))
    scheduler.submit_pod(Pod(
        name="api-server-1",
        namespace="default",
        resource_requests=Resources(cpu_millicores=1000, memory_mb=2048),
        resource_limits=Resources(cpu_millicores=2000, memory_mb=4096)
    ))
    
    # Schedule pods
    print("\nScheduling pods...")
    scheduled = scheduler.schedule_pending_pods()
    print(f"  Scheduled {len(scheduled)} pods: {scheduled}")
    
    # Show node status
    print("\nNode status:")
    for status in scheduler.get_node_status():
        print(f"  {status['name']}:")
        print(f"    CPU: {status['available_cpu']}/{status['total_cpu']} millicores available")
        print(f"    Memory: {status['available_memory']}/{status['total_memory']} MB available")
        print(f"    Pods: {status['pod_count']}")
    
    # Show pod assignments
    print("\nPod assignments:")
    for pod_name, pod in scheduler.pods.items():
        if pod.assigned_node:
            print(f"  {pod_name} -> {pod.assigned_node}")

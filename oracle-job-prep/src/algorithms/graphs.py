"""
Graph Algorithms for Oracle Interview Preparation

This module implements essential graph algorithms commonly asked in
technical interviews, including BFS, DFS, shortest paths, and more.
"""

from typing import List, Dict, Set, Optional, Tuple
from collections import deque, defaultdict
import heapq


class Graph:
    """
    Graph data structure with both adjacency list and adjacency matrix support.
    Supports both directed and undirected graphs.
    """
    
    def __init__(self, directed: bool = False):
        """
        Initialize a graph.
        
        Args:
            directed: If True, creates a directed graph; otherwise undirected
        """
        self.graph = defaultdict(list)
        self.directed = directed
        self.vertices = set()
    
    def add_edge(self, u: int, v: int, weight: int = 1):
        """
        Add an edge to the graph.
        
        Args:
            u: Source vertex
            v: Destination vertex
            weight: Edge weight (default 1)
        """
        self.graph[u].append((v, weight))
        self.vertices.add(u)
        self.vertices.add(v)
        
        if not self.directed:
            self.graph[v].append((u, weight))
    
    def bfs(self, start: int) -> List[int]:
        """
        Breadth-First Search traversal.
        
        Time Complexity: O(V + E)
        Space Complexity: O(V)
        
        Args:
            start: Starting vertex
            
        Returns:
            List of vertices in BFS order
        """
        visited = set()
        queue = deque([start])
        result = []
        
        visited.add(start)
        
        while queue:
            vertex = queue.popleft()
            result.append(vertex)
            
            for neighbor, _ in self.graph[vertex]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return result
    
    def dfs(self, start: int) -> List[int]:
        """
        Depth-First Search traversal (iterative).
        
        Time Complexity: O(V + E)
        Space Complexity: O(V)
        
        Args:
            start: Starting vertex
            
        Returns:
            List of vertices in DFS order
        """
        visited = set()
        stack = [start]
        result = []
        
        while stack:
            vertex = stack.pop()
            
            if vertex not in visited:
                visited.add(vertex)
                result.append(vertex)
                
                # Add neighbors in reverse order for correct DFS order
                for neighbor, _ in reversed(self.graph[vertex]):
                    if neighbor not in visited:
                        stack.append(neighbor)
        
        return result
    
    def dfs_recursive(self, start: int, visited: Optional[Set[int]] = None) -> List[int]:
        """
        Depth-First Search traversal (recursive).
        
        Args:
            start: Starting vertex
            visited: Set of visited vertices (used internally)
            
        Returns:
            List of vertices in DFS order
        """
        if visited is None:
            visited = set()
        
        result = []
        visited.add(start)
        result.append(start)
        
        for neighbor, _ in self.graph[start]:
            if neighbor not in visited:
                result.extend(self.dfs_recursive(neighbor, visited))
        
        return result
    
    def has_cycle(self) -> bool:
        """
        Detect if the graph has a cycle.
        
        Returns:
            True if cycle exists, False otherwise
        """
        visited = set()
        rec_stack = set()
        
        def has_cycle_util(v: int) -> bool:
            visited.add(v)
            rec_stack.add(v)
            
            for neighbor, _ in self.graph[v]:
                if neighbor not in visited:
                    if has_cycle_util(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(v)
            return False
        
        for vertex in self.vertices:
            if vertex not in visited:
                if has_cycle_util(vertex):
                    return True
        
        return False
    
    def topological_sort(self) -> Optional[List[int]]:
        """
        Topological sorting using DFS.
        Only works for Directed Acyclic Graphs (DAG).
        
        Returns:
            List of vertices in topological order, or None if cycle exists
        """
        if not self.directed or self.has_cycle():
            return None
        
        visited = set()
        stack = []
        
        def topological_sort_util(v: int):
            visited.add(v)
            
            for neighbor, _ in self.graph[v]:
                if neighbor not in visited:
                    topological_sort_util(neighbor)
            
            stack.append(v)
        
        for vertex in self.vertices:
            if vertex not in visited:
                topological_sort_util(vertex)
        
        return stack[::-1]
    
    def dijkstra(self, start: int) -> Dict[int, int]:
        """
        Dijkstra's shortest path algorithm.
        
        Time Complexity: O((V + E) log V) with min heap
        
        Args:
            start: Starting vertex
            
        Returns:
            Dictionary mapping vertices to shortest distances from start
        """
        distances = {vertex: float('infinity') for vertex in self.vertices}
        distances[start] = 0
        
        pq = [(0, start)]  # (distance, vertex)
        visited = set()
        
        while pq:
            current_dist, current = heapq.heappop(pq)
            
            if current in visited:
                continue
            
            visited.add(current)
            
            for neighbor, weight in self.graph[current]:
                distance = current_dist + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    heapq.heappush(pq, (distance, neighbor))
        
        return distances
    
    def bellman_ford(self, start: int) -> Tuple[Dict[int, int], bool]:
        """
        Bellman-Ford algorithm for shortest paths (handles negative weights).
        
        Time Complexity: O(V * E)
        
        Args:
            start: Starting vertex
            
        Returns:
            Tuple of (distances dictionary, has_negative_cycle boolean)
        """
        distances = {vertex: float('infinity') for vertex in self.vertices}
        distances[start] = 0
        
        # Relax edges |V| - 1 times
        for _ in range(len(self.vertices) - 1):
            for u in self.vertices:
                for v, weight in self.graph[u]:
                    if distances[u] + weight < distances[v]:
                        distances[v] = distances[u] + weight
        
        # Check for negative cycles
        has_negative_cycle = False
        for u in self.vertices:
            for v, weight in self.graph[u]:
                if distances[u] + weight < distances[v]:
                    has_negative_cycle = True
                    break
        
        return distances, has_negative_cycle
    
    def floyd_warshall(self) -> Dict[int, Dict[int, int]]:
        """
        Floyd-Warshall algorithm for all-pairs shortest paths.
        
        Time Complexity: O(V³)
        Space Complexity: O(V²)
        
        Returns:
            Dictionary of dictionaries with shortest distances between all pairs
        """
        # Initialize distances
        dist = {}
        vertices_list = list(self.vertices)
        
        for i in vertices_list:
            dist[i] = {}
            for j in vertices_list:
                if i == j:
                    dist[i][j] = 0
                else:
                    dist[i][j] = float('infinity')
        
        # Set direct edge weights
        for u in self.vertices:
            for v, weight in self.graph[u]:
                dist[u][v] = weight
        
        # Floyd-Warshall algorithm
        for k in vertices_list:
            for i in vertices_list:
                for j in vertices_list:
                    if dist[i][j] > dist[i][k] + dist[k][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
        
        return dist
    
    def is_bipartite(self) -> bool:
        """
        Check if graph is bipartite using BFS.
        
        Returns:
            True if graph is bipartite, False otherwise
        """
        color = {}
        
        for start in self.vertices:
            if start in color:
                continue
            
            queue = deque([start])
            color[start] = 0
            
            while queue:
                vertex = queue.popleft()
                
                for neighbor, _ in self.graph[vertex]:
                    if neighbor not in color:
                        color[neighbor] = 1 - color[vertex]
                        queue.append(neighbor)
                    elif color[neighbor] == color[vertex]:
                        return False
        
        return True


def find_strongly_connected_components(graph: Graph) -> List[List[int]]:
    """
    Find all strongly connected components using Kosaraju's algorithm.
    
    Time Complexity: O(V + E)
    
    Args:
        graph: Directed graph
        
    Returns:
        List of strongly connected components
    """
    visited = set()
    stack = []
    
    # First DFS to fill stack
    def fill_order(v: int):
        visited.add(v)
        for neighbor, _ in graph.graph[v]:
            if neighbor not in visited:
                fill_order(neighbor)
        stack.append(v)
    
    for vertex in graph.vertices:
        if vertex not in visited:
            fill_order(vertex)
    
    # Create reversed graph
    reversed_graph = Graph(directed=True)
    for u in graph.vertices:
        for v, weight in graph.graph[u]:
            reversed_graph.add_edge(v, u, weight)
    
    # Second DFS on reversed graph
    visited.clear()
    sccs = []
    
    def dfs_scc(v: int, component: List[int]):
        visited.add(v)
        component.append(v)
        for neighbor, _ in reversed_graph.graph[v]:
            if neighbor not in visited:
                dfs_scc(neighbor, component)
    
    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            component = []
            dfs_scc(vertex, component)
            sccs.append(component)
    
    return sccs


if __name__ == "__main__":
    # Example usage
    print("Graph Algorithms Demo\n")
    
    # Create a directed graph
    g = Graph(directed=True)
    g.add_edge(0, 1, 4)
    g.add_edge(0, 2, 1)
    g.add_edge(2, 1, 2)
    g.add_edge(1, 3, 1)
    g.add_edge(2, 3, 5)
    
    print("BFS from vertex 0:", g.bfs(0))
    print("DFS from vertex 0:", g.dfs(0))
    print("Has cycle:", g.has_cycle())
    print("Topological Sort:", g.topological_sort())
    
    print("\nDijkstra's shortest paths from vertex 0:")
    distances = g.dijkstra(0)
    for vertex, dist in sorted(distances.items()):
        print(f"  To vertex {vertex}: {dist}")

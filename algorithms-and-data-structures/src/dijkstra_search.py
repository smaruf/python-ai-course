import sys
import unittest

class Graph:
    """Weighted undirected graph represented as an adjacency matrix.

    Supports Dijkstra's shortest-path algorithm for finding the minimum
    distance from a source vertex to every other vertex in the graph.

    Attributes:
        V (int): Number of vertices in the graph.
        graph (list[list[int]]): V×V adjacency matrix where ``graph[u][v]``
            holds the edge weight between vertices ``u`` and ``v``, or 0 if
            no edge exists.
    """

    def __init__(self, vertices):
        """Initialise an empty graph with the given number of vertices.

        Args:
            vertices (int): Total number of vertices.
        """
        self.V = vertices
        self.graph = [[0 for column in range(vertices)] for row in range(vertices)]
    
    def min_distance(self, dist, spt_set):
        """Return the index of the unvisited vertex with the smallest distance.

        Scans the distance array and returns the vertex that has the minimum
        tentative distance and has not yet been added to the shortest-path
        tree (SPT).

        Args:
            dist (list[int]): Current shortest-distance estimates for every
                vertex.
            spt_set (list[bool]): Boolean flags indicating whether each vertex
                has been finalised in the SPT.

        Returns:
            int: Index of the closest unvisited vertex, or -1 if all
            remaining vertices are unreachable.
        """
        min = sys.maxsize
        min_index = -1
        for v in range(self.V):
            if dist[v] < min and not spt_set[v]:
                min, min_index = dist[v], v
        return min_index
    
    def dijkstra(self, src):
        """Compute shortest distances from *src* to all other vertices.

        Implements Dijkstra's algorithm using an adjacency matrix and a
        linear-scan minimum selection (O(V²) time complexity).  All edge
        weights must be non-negative.

        Args:
            src (int): Index of the source vertex (0-based).  Must be in the
                range ``[0, V)``.

        Returns:
            list[int]: A list of length ``V`` where the value at index ``i``
            is the shortest distance from ``src`` to vertex ``i``.  Vertices
            that are not reachable from ``src`` will have a value of
            ``sys.maxsize``.

        Raises:
            IndexError: If ``src`` is outside the range ``[0, V)``.

        Example:
            >>> g = Graph(3)
            >>> g.graph = [[0, 1, 4], [1, 0, 2], [4, 2, 0]]
            >>> g.dijkstra(0)
            [0, 1, 3]
        """
        dist = [sys.maxsize] * self.V
        dist[src] = 0
        spt_set = [False] * self.V
        
        for cout in range(self.V):
            u = self.min_distance(dist, spt_set)
            spt_set[u] = True

            for v in range(self.V):
                if self.graph[u][v] > 0 and not spt_set[v] and dist[v] > dist[u] + self.graph[u][v]:
                    dist[v] = dist[u] + self.graph[u][v]
        
        return dist

# Unit tests for the Graph's Dijkstra algorithm
class TestDijkstraAlgorithm(unittest.TestCase):
    def setUp(self):
        self.graph = Graph(10)
        self.graph.graph = [
            [0, 3, 0, 0, 0, 0, 0, 8, 0, 0], 
            [3, 0, 1, 0, 0, 0, 0, 0, 0, 0], 
            [0, 1, 0, 7, 0, 4, 0, 0, 2, 0], 
            [0, 0, 7, 0, 9, 14, 0, 0, 0, 0], 
            [0, 0, 0, 9, 0, 10, 0, 0, 0, 0], 
            [0, 0, 4, 14, 10, 0, 2, 0, 0, 0], 
            [0, 0, 0, 0, 0, 2, 0, 1, 6, 0], 
            [8, 0, 0, 0, 0, 0, 1, 0, 0, 0], 
            [0, 0, 2, 0, 0, 0, 6, 0, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]

    def test_standard_case(self):
        expected_result = [0, 3, 9, 22, 31, 18, 18, 8, 11, sys.maxsize]
        result = self.graph.dijkstra(0)
        self.assertEqual(result, expected_result)

    def test_isolated_node(self):
        expected_result = [sys.maxsize] * 9 + [0]
        result = self.graph.dijkstra(9)
        self.assertEqual(result, expected_result)

    def test_node_out_of_bounds(self):
        with self.assertRaises(IndexError):
            self.graph.dijkstra(10)

if __name__ == '__main__':
    unittest.main()

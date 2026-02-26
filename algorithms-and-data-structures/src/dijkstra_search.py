import sys
import unittest

class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = [[0 for column in range(vertices)] for row in range(vertices)]
    
    def min_distance(self, dist, spt_set):
        min = sys.maxsize
        min_index = -1
        for v in range(self.V):
            if dist[v] < min and not spt_set[v]:
                min, min_index = dist[v], v
        return min_index
    
    def dijkstra(self, src):
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

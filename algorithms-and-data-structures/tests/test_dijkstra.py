import unittest

class TestDijkstraAlgorithm(unittest.TestCase):
    def setUp(self):
        # Given: Setup a 10x10 graph
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

    def test_dijkstra_algorithm_basic_case(self):
        # When: Run from node 0
        result = self.graph.dijkstra(0)
        # Then: Compare to expected results
        expected = [0, 3, 9, 22, 31, 18, 18, 8, 11, sys.maxsize]
        self.assertEqual(result, expected)

    def test_dijkstra_algorithm_edge_case(self):
        # When: Run from node 9 (only self-connects, isolated node)
        result = self.graph.dijkstra(9)
        # Then: Compare to expected results
        expected = [sys.maxsize] * 9 + [0]
        self.assertEqual(result, expected)

    def test_dijkstra_algorithm_non_existent_node(self):
        # When/Then: Trying to run from a node not in graph
        with self.assertRaises(IndexError):
            self.graph.dijkstra(10)  # This should raise IndexError
    
if __name__ == '__main__':
    unittest.main()

import sys

class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = [[0 for column in range(vertices)] for row in range(vertices)]
    
    def print_solution(self, dist):
        print("Vertex Distance from Source")
        for node in range(self.V):
            print(node, ":", dist[node])
    
    def min_distance(self, dist, spt_set):
        min = sys.maxsize
        
        for v in range(self.V):
            if dist[v] < min and not spt_set[v]:
                min = dist[v]
                min_index = v
                
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
        
        self.print_solution(dist)

# Example usage:
# g = Graph(9)
# g.graph = [[...], [...], ...]
# g.dijkstra(0)

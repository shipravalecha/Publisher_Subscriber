from time import time
class Graph:
 
    def __init__(self):
        self.V = 0 # No. of vertices
        self.graph = []
        self.verticesSet = set([])
        self.weight_dict = {}   
        self.timestamp_dict = {} 
        self.parent_dict = {} 
    # function to add an edge to graph
    def addEdge(self, u, v, w, timestamp):
        
        self.weight_dict[(u,v)] = w
        # add reverse edge with negative log
        self.weight_dict[(v, u)] = -w
        #update tiemstamps
        self.timestamp_dict[(u, v)] = timestamp
        self.timestamp_dict[(v, u)] = timestamp
        
        edges = []
        current_timestamp = time()*1000
        staled_quotes = []
        for key in self.weight_dict:
            val = self.weight_dict[key]
            timestamp = self.timestamp_dict[key]
            # append only edges which are seen in the last 1.5 seconds
            if current_timestamp - timestamp <=1500:
                edges.append((key[0], key[1], val))
            else:
                staled_quotes.append(key)
                print(f"Discarding scale quote: {key[0]} -> {key[1]} at timestamp {timestamp} for current timestamp {current_timestamp}")
        
        for quote in staled_quotes:
            self.weight_dict.pop(quote, None)
            self.timestamp_dict.pop(quote, None)

        self.graph = edges
        self.verticesSet.add(u)
        self.verticesSet.add(v)
        self.V = len(self.verticesSet)
    # utility function used to print the solution
    def printArr(self, dist):
        print("Vertex Distance from Source")
        for i in self.verticesSet:
            print("{0}\t\t{1}".format(i, dist[i]))
 
    # The main function that finds shortest distances from src to
    # all other vertices using Bellman-Ford algorithm. The function
    # also detects negative weight cycle
    def BellmanFord(self, src, tolerance=0.0007):
 
        # Step 1: Initialize distances from src to all other vertices
        # as INFINITE
        dist = {}
        sequence = []
        for i in self.verticesSet:
            dist[i] = float("Inf")
        dist[src] = 0
 
        # Step 2: Relax all edges |V| - 1 times. A simple shortest
        # path from src to any other vertex can have at-most |V| - 1
        # edges
        for _ in range(self.V - 1):
            # Update dist value and parent index of the adjacent vertices of
            # the picked vertex. Consider only those vertices which are still in
            # queue
            for u, v, w in self.graph:
                if dist[u] != float("Inf") and dist[u] + w < dist[v]:
                    sequence.append((u, v, w))
                    dist[v] = dist[u] + w
                    self.parent_dict[v] = u
        # Step 3: check for negative-weight cycles. The above step
        # guarantees shortest distances if graph doesn't contain
        # negative weight cycle. If we get a shorter path, then there
        # is a cycle.
        for u, v, w in self.graph:
            if dist[u] != float("Inf") and dist[u] + w < dist[v]:
                print("ARBITRAGE")
                self.printCycle(v, u)
                return
        # print all distance
        self.printArr(dist)
    def printCycle(self, v, u):

        start = u
        res = [v]
        print("Printing cycle")
        while True:
            if start in res:
                res.append(start)
                break
            res.append(start)
            start = self.parent_dict[start]
        for i in range(1, len(res)):
            u = res[i]
            v = res[i - 1]
            key = (u, v)
            print(key)
            print(self.weight_dict[key])
            print(f"{res[i - 1]} -> ")



    
    
# Driver's code
if __name__ == '__main__':
    g = Graph(5)
    g.addEdge(0, 1, -1)
    g.addEdge(2, 0, -4)
    g.addEdge(1, 2, 3)
    g.addEdge(1, 3, 2)
    g.addEdge(1, 4, 2)
    g.addEdge(3, 2, 5)
    g.addEdge(3, 1, 1)
    g.addEdge(4, 3, -3)
    g.addEdge(2, 4, -1)
    print('in bellaman')
 
    # function call
    g.BellmanFord(0)
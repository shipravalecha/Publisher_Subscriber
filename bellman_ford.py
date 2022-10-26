"""
bellamn_ford.py
CPSC 5520, Seattle University
This is the bellamn_ford algorithm that detects the negative cycle in the graph. It takes source currency as input
and runs the bellman ford algorithm. It takes the source currency, destination currency and weights from the lab3 and
creates the edges for the graph.
:Authors: Fnu Shipra
:Version: 0.0
"""

from time import time
class Graph:
    
    """
    Init method is used to initialize the variables, dictionaries, lists that are used in the program.
    """
    def __init__(self):
        self.V = 0                                                                  # No. of vertices
        self.graph = []                                                             # Graph dictionary
        self.verticesSet = set([])                                                  # vertices set to determine the number of iterations of the graph
        self.weight_dict = {}                                                       # dictionary to store weights
        self.timestamp_dict = {}                                                    # dictionary to store timestamps
        self.parent_dict = {}                                                       # dictionary to store parents of nodes
        self.exchange_dict = {}                                                     # dictionary to store exchange rates
    
    """
    This method is used to add the edges in the graph by taking source currency, 
    destination currency and weights as inputs
    """
    def addEdge(self, u, v, w, timestamp, rate):
        
        self.weight_dict[(u,v)] = w                                                 # add the edge with log value i.e. w = log(rate)
        self.weight_dict[(v, u)] = -w                                               # add the reverse edge with negative log i.e. w = -log(rate)
        self.timestamp_dict[(u, v)] = timestamp                                     # update tiemstamps
        self.timestamp_dict[(v, u)] = timestamp
        self.exchange_dict[(u, v)]  = rate                                          # update exchange rates u -> v = rate
        self.exchange_dict[(v, u)]  = 1 / rate                                      # update exchange rates v -> u = 1/rate
        edges = []
        current_timestamp = time() * 1000
        staled_quotes = []                                                          # list to keep track of staled records 

        for key in self.weight_dict:
            weight = self.weight_dict[key]
            timestamp = self.timestamp_dict[key]

            if current_timestamp - timestamp <= 1500:                               # append only edges which are seen in the last 1.5 seconds
                edges.append((key[0], key[1], weight))
            else:                                                                   # else discard the stale records
                staled_quotes.append(key)
                print(f"Discarding scale quote: {key[0]} -> {key[1]}")

        for quote in staled_quotes:                                                 # remove staled records from  dictionaries as well
            self.weight_dict.pop(quote, None)
            self.timestamp_dict.pop(quote, None)

        self.graph = edges
        self.verticesSet.add(u)
        self.verticesSet.add(v)
        self.V = len(self.verticesSet)
    
    """
    This is the method that runs the bellamn ford algorithm to find the shortest distance from source node 
    to all other nodes. This method also detects the negative cycle. 
    """
    def BellmanFord(self, src, tolerance=0.01):                    # used the tolerance of around 0.01
 
        dist = {}
        sequence = []
        for i in self.verticesSet:                                 # Initialize distances from src to all other vertices as infinity
            dist[i] = float("Inf")
        dist[src] = 0
 
        # Relax all edges |V| - 1 times. A simple shortest
        # path from src to any other vertex can have at-most |V| - 1
        # edges
        for _ in range(self.V - 1):                                # update the distance of the source vertex i.e. u as per the relaxation condition. Also update the paren node
            for u, v, w in self.graph:
                if dist[u] != float("Inf") and dist[u] + w < dist[v] :
                    sequence.append((u, v, w))
                    dist[v] = dist[u] + w
                    self.parent_dict[v] = u
        
        # Check for negative-weight cycles. The above step guarantees shortest distances if graph doesn't contain
        # negative weight cycle. If in this iteration the weight changes,then there is a negative weight cycle.
        for u, v, w in self.graph:
            if dist[u] != float("Inf") and dist[u] + w < dist[v] and abs(dist[v] - (dist[u] + w)) > tolerance:
                print("ARBITRAGE")
                self.printCycle(v, u)
                return

    """
    This method prints the negative cycle with the format as source currency, destination currency and their exhange rates
    """
    def printCycle(self, v, u):
        start = u
        res = [v]
        while True:
            if start in res:
                res.append(start)
                break
            res.append(start)
            start = self.parent_dict[start]
        start_currency = 100
        print(f"starting with  : {start_currency} {res[len(res) - 1]}")

        for i in range(len(res) - 1, 0, -1):
            u = res[i]
            v = res[i - 1]
            key = (u, v)
            exchange_rate =  self.exchange_dict[key]
            print(f"Exchanged {u} -> {v} at rate {exchange_rate}")
            print(f"current currency: {start_currency * exchange_rate} {v}")
            start_currency = start_currency * exchange_rate

from collection import defaultdict
import heapq


class Graph:
    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(list)

    def add_node(self, value):
        self.nodes.add(value)

    def add_edges(self, from_node, to_node, weight):
        self.edges[from_node].append([to_node, weight])


def dijkstra(graph, start_node):
    visited = {start_node: 0}
    nodes = set(graph.nodes)
    path = {}

    while nodes:
        min_node = None
        min_weight = 0
        for node in nodes:
            if node in visited:
                if not min_node or min_weight > visited[node]:
                    min_node = node
                    min_weight = visited[node]

        for to_node, weight in graph.edges[min_node]:
            if to_node not in visited or visited[to_node] > weight + min_weight:
                visited[to_node] = weight + min_weight
                path[to_node] = min_node
        nodes.remove(min_node)
    return path

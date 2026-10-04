"""
Core algorithms for the Smart Route Finder (DAA CIA3 prototype).

Everything here is written from scratch - no networkx / library shortest-path
functions are used for the algorithm itself.

Graph format (adjacency list):
    graph = {
        "A": [("B", 4), ("C", 2)],
        "B": [("A", 4)],
        ...
    }
Each tuple is (neighbour, weight).
"""

import heapq
from collections import deque


# --------------------------------------------------------------------------
# 1. Dijkstra's Algorithm (min-heap implementation)
# --------------------------------------------------------------------------
def dijkstra(graph, source, target=None):
    """
    Single-source shortest paths on a graph with NON-NEGATIVE edge weights.

    Returns
    -------
    dist  : dict  node -> shortest distance from source (inf if unreachable)
    prev  : dict  node -> previous node on the shortest path (for path rebuild)
    steps : list  one record per node *finalised*, used for the step-by-step
                  trace shown in the app and the report.

    Time complexity : O((V + E) log V) with a binary min-heap
    Space complexity: O(V + E)

    If `target` is given, the search stops early as soon as the target is
    finalised (it is then guaranteed to have its final shortest distance).
    """
    for u, edges in graph.items():
        for v, w in edges:
            if w < 0:
                raise ValueError(
                    f"Negative edge weight on {u}->{v}. "
                    "Dijkstra's algorithm does not support negative weights."
                )

    dist = {node: float("inf") for node in graph}
    prev = {node: None for node in graph}
    dist[source] = 0

    heap = [(0, source)]          # (distance, node) - heapq gives a min-heap
    visited = set()
    steps = []

    while heap:
        d, u = heapq.heappop(heap)

        # Lazy deletion: skip stale heap entries for nodes already finalised
        if u in visited:
            continue
        visited.add(u)

        relaxed = []              # edges that improved a distance this step
        for v, w in graph[u]:
            if v in visited:
                continue
            new_d = d + w
            if new_d < dist[v]:   # RELAXATION
                dist[v] = new_d
                prev[v] = u
                heapq.heappush(heap, (new_d, v))
                relaxed.append((v, new_d))

        steps.append(
            {
                "step": len(steps) + 1,
                "visited_node": u,
                "distance": d,
                "relaxed": relaxed,
                "snapshot": dict(dist),   # distances after this step
            }
        )

        if target is not None and u == target:
            break

    return dist, prev, steps


def reconstruct_path(prev, source, target):
    """Walk the predecessor map backwards from target to source."""
    path = []
    node = target
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()
    if not path or path[0] != source:
        return []                 # target is unreachable from source
    return path


# --------------------------------------------------------------------------
# 2. BFS (hop-count shortest path) - used for the comparison
# --------------------------------------------------------------------------
def bfs_path(graph, source, target):
    """
    Shortest path by NUMBER OF EDGES (ignores weights).
    Returns the path as a list of nodes ([] if unreachable).
    Time complexity: O(V + E)
    """
    prev = {source: None}
    queue = deque([source])
    while queue:
        u = queue.popleft()
        if u == target:
            break
        for v, _ in graph[u]:
            if v not in prev:
                prev[v] = u
                queue.append(v)
    if target not in prev:
        return []
    path, node = [], target
    while node is not None:
        path.append(node)
        node = prev[node]
    return path[::-1]


def path_weight(graph, path):
    """Total weight of a path given as a list of nodes."""
    total = 0
    for a, b in zip(path, path[1:]):
        total += next(w for v, w in graph[a] if v == b)
    return total


# --------------------------------------------------------------------------
# 3. Helper: build an adjacency list from an undirected edge list
# --------------------------------------------------------------------------
def build_graph(nodes, edges):
    graph = {n: [] for n in nodes}
    for a, b, w in edges:
        graph[a].append((b, w))
        graph[b].append((a, w))   # undirected: roads work both ways
    return graph

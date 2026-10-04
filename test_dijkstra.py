"""
Correctness tests: our from-scratch Dijkstra is checked against networkx
(networkx is used ONLY here, as an independent reference).

Run with:  python test_dijkstra.py
"""

import itertools

import networkx as nx

from dijkstra import bfs_path, build_graph, dijkstra, path_weight, reconstruct_path
from graph_data import EDGES, NODES, load_graph


def test_all_pairs_match_networkx():
    graph = load_graph()
    G = nx.Graph()
    G.add_weighted_edges_from(EDGES)

    checked = 0
    for s, t in itertools.permutations(NODES, 2):
        dist, prev, _ = dijkstra(graph, s, t)
        path = reconstruct_path(prev, s, t)
        expected = nx.dijkstra_path_length(G, s, t)
        assert dist[t] == expected, f"{s}->{t}: got {dist[t]}, expected {expected}"
        assert path[0] == s and path[-1] == t
        assert path_weight(graph, path) == expected
        checked += 1
    print(f"PASS  all {checked} source/target pairs match networkx")


def test_full_run_without_target():
    graph = load_graph()
    G = nx.Graph()
    G.add_weighted_edges_from(EDGES)
    dist, _, steps = dijkstra(graph, "Majestic")
    ref = nx.single_source_dijkstra_path_length(G, "Majestic")
    assert dist == ref
    assert len(steps) == len(NODES)
    print("PASS  full single-source run matches networkx")


def test_unreachable_node():
    g = build_graph(["A", "B", "C"], [("A", "B", 1)])
    dist, prev, _ = dijkstra(g, "A", "C")
    assert dist["C"] == float("inf")
    assert reconstruct_path(prev, "A", "C") == []
    print("PASS  unreachable node handled")


def test_negative_weight_rejected():
    g = {"A": [("B", -1)], "B": []}
    try:
        dijkstra(g, "A")
    except ValueError:
        print("PASS  negative weight rejected")
        return
    raise AssertionError("negative weight should raise ValueError")


def test_bfs_can_be_wrong_on_weighted_graph():
    # A-D direct is 1 hop but 10 m; A-B-C-D is 3 hops but 3 m
    g = build_graph(["A", "B", "C", "D"],
                    [("A", "D", 10), ("A", "B", 1), ("B", "C", 1), ("C", "D", 1)])
    d_path = reconstruct_path(dijkstra(g, "A", "D")[1], "A", "D")
    b_path = bfs_path(g, "A", "D")
    assert path_weight(g, d_path) == 3
    assert path_weight(g, b_path) == 10
    print("PASS  BFS ignores weights, Dijkstra does not")


if __name__ == "__main__":
    test_all_pairs_match_networkx()
    test_full_run_without_target()
    test_unreachable_node()
    test_negative_weight_rejected()
    test_bfs_can_be_wrong_on_weighted_graph()
    print("\nAll tests passed.")

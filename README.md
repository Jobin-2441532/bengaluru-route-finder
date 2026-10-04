# Bengaluru Smart Route Finder: Dijkstra's Algorithm

**Course:** Design and Analysis of Algorithms (DAA) · **Assessment:** CIA3 Prototype Development

A small working prototype that finds the shortest route between two places in
Bengaluru using **Dijkstra's algorithm**, implemented from scratch with a
binary min-heap. The app draws the route on a map of the city, explains every
step of the algorithm, and compares it with BFS to show why road lengths matter.

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py          # opens the web app in your browser
python test_dijkstra.py       # correctness tests (optional)
```

## Files

| File | Purpose |
|---|---|
| `dijkstra.py` | The algorithms: Dijkstra (from scratch), BFS (for comparison), path rebuild |
| `graph_data.py` | The Bengaluru map: 25 landmarks (GPS coordinates), 43 main-road links, distance estimates |
| `app.py` | Streamlit interface: dropdowns, map with highlighted route, step table, BFS comparison |
| `test_dijkstra.py` | Checks Dijkstra against networkx on all 600 source/destination pairs |

## About the map data (important, be ready to explain this)

- **Places:** 25 real Bengaluru localities and landmarks (Majestic, MG Road, Koramangala, CHRIST University, Whitefield, Electronic City, ...) at approximate GPS coordinates.
- **Roads:** a link between two places means they are directly connected by a main road (Hosur Road, Outer Ring Road, Old Airport Road, Mysore Road, Tumkur Road, etc.). Only major connections are included, not every street.
- **Distances:** estimated as straight-line distance (haversine formula) × 1.3, a common rule of thumb for how much longer city roads are than a straight line. They are **approximate, not surveyed road distances**, and do not include traffic.
- To use exact distances, add measured values to `WEIGHT_OVERRIDES` in `graph_data.py`.

## Problem statement

Given a weighted road network of Bengaluru, find the shortest route from a chosen start to a chosen destination.

## How the algorithm works

1. Set the distance to the start = 0 and every other place = ∞.
2. Put the start in a min-heap.
3. Repeatedly remove the place with the **smallest known distance** and mark it final (greedy choice).
4. For each neighbour, check if going through this place is shorter. If so, update it (**relaxation**) and push it to the heap.
5. Store each place's predecessor so the actual route can be rebuilt backwards from the destination.
6. Stop when the destination is finalised.

**Why the greedy choice is correct:** with non-negative weights, any other route to a not-yet-final place must pass through a place at least as far away, so it can never be shorter.

## Complexity

| | Dijkstra (binary heap) | BFS |
|---|---|---|
| Time | O((V + E) log V) | O(V + E) |
| Space | O(V + E) | O(V) |
| Handles weights | Yes (non-negative) | No (segment count only) |

V = number of places (25), E = number of roads (43). Without a heap (plain array scan) Dijkstra is O(V²).

## Limitations

- Does not work with negative edge weights (use Bellman-Ford); the code raises an error if it finds one.
- Distances are estimates, only main roads are modelled, and there is no live traffic. Travel time uses a flat average speed of 20 km/h.
- Future scope: load the full road network from OpenStreetMap (e.g. with the `osmnx` library) and use A* with straight-line distance as the heuristic.

## Likely viva questions

- **Why a min-heap?** To get the closest unvisited place in O(log V) instead of scanning all V places.
- **Why can't Dijkstra handle negative weights?** A finalised place's distance could later be beaten via a negative edge, breaking the greedy assumption.
- **Why does the code skip already-visited nodes after popping?** Lazy deletion: instead of decreasing a key in the heap, we push a new entry and ignore stale ones.
- **How is this different from BFS?** BFS minimises the number of road segments; Dijkstra minimises total distance. They agree only when all roads have equal length. Try CHRIST University → Whitefield in the app: BFS is about 5.6 km longer.
- **Where do your distances come from?** GPS coordinates + haversine formula × 1.3 circuity factor (approximate; see "About the map data").
- **What if a place is unreachable?** Its distance stays ∞ and the app reports that no route exists.
- **Is it greedy or dynamic programming?** Greedy (with optimal substructure: sub-paths of a shortest path are themselves shortest).
- **Real-world uses:** GPS navigation, network routing (OSPF), logistics.

## Report outline (suggested)

1. Problem statement and objective
2. Algorithm explanation with a small worked example (use the step table from the app)
3. Design: data structures (adjacency list, min-heap, predecessor map) and how the map data was built
4. Implementation: screenshots of the app for 2-3 different routes
5. Testing: output of `python test_dijkstra.py`, BFS vs Dijkstra comparison
6. Complexity analysis, limitations, future scope (real road data, live traffic, A*)

## Customising the map

Edit `LANDMARKS` (name → latitude, longitude) and `ROADS` (pairs of directly connected places) in `graph_data.py`. For a new place, also add a label position in `LABEL_POS` in `app.py` (optional; it defaults to below the dot). Everything else updates automatically.

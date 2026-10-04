"""
Bengaluru Smart Route Finder - DAA CIA3 prototype
Algorithm: Dijkstra's shortest path (implemented from scratch in dijkstra.py)

Run with:  streamlit run app.py
"""

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from dijkstra import bfs_path, dijkstra, path_weight, reconstruct_path
from graph_data import CIRCUITY, EDGES, POSITIONS, load_graph

AVG_SPEED_KMPH = 20  # rough average city speed in Bengaluru traffic

st.set_page_config(page_title="Bengaluru Route Finder", page_icon="🧭", layout="wide")

graph = load_graph()
places = sorted(graph.keys())


def km(metres):
    return f"{metres / 1000:.1f}"


# ------------------------------------------------------------------ header
st.title("🧭 Bengaluru Smart Route Finder")
st.caption(
    "Shortest-path navigation across Bengaluru using **Dijkstra's Algorithm** "
    "(min-heap implementation, written from scratch) · Design and Analysis of Algorithms"
)

# ----------------------------------------------------------------- controls
c1, c2, c3 = st.columns([2, 2, 1])
source = c1.selectbox("From", places, index=places.index("CHRIST University"))
target = c2.selectbox("To", places, index=places.index("Whitefield"))
c3.write("")
c3.write("")
c3.button("Find Route", type="primary", width="stretch")

if source == target:
    st.info("Pick two different locations.")
    st.stop()

# ------------------------------------------------------------------ compute
dist, prev, steps = dijkstra(graph, source, target)
path = reconstruct_path(prev, source, target)

if not path:
    st.error("No route exists between these two locations.")
    st.stop()

total = dist[target]
m1, m2, m3 = st.columns(3)
m1.metric("Shortest distance", f"{km(total)} km")
m2.metric("Stops on route", len(path))
m3.metric(f"Est. travel time (~{AVG_SPEED_KMPH} km/h)", f"{total / 1000 / AVG_SPEED_KMPH * 60:.0f} min")
st.success("  →  ".join(path))

# --------------------------------------------------------------------- map
# where to put each place name relative to its dot (keeps labels from overlapping)
LABEL_POS = {
    "Majestic": "left", "Cubbon Park": "above", "MG Road": "below",
    "Ulsoor Lake": "above", "Indiranagar": "above", "Domlur": "right",
    "Koramangala": "right", "CHRIST University": "left", "Lalbagh": "right",
    "Jayanagar": "below", "Basavanagudi": "left", "Banashankari": "below",
    "JP Nagar": "below", "BTM Layout": "below", "Silk Board": "above",
    "HSR Layout": "below", "Bellandur": "below", "Marathahalli": "below",
    "Whitefield": "below", "KR Puram": "above", "Electronic City": "below",
    "Hebbal": "above",
    "Yeshwanthpur": "left", "Rajajinagar": "left", "Malleshwaram": "left",
}
OFFSETS = {  # (x, y) offset in points, horizontal align, vertical align
    "below": ((0, -9), "center", "top"),
    "above": ((0, 9), "center", "bottom"),
    "left": ((-9, 0), "right", "center"),
    "right": ((9, 0), "left", "center"),
}
OUTLINE = [pe.withStroke(linewidth=3, foreground="white")]


def draw_map(highlight_path, show_all_distances):
    fig, ax = plt.subplots(figsize=(9, 8.6))
    on_path = set(highlight_path)
    route_edges = {tuple(sorted(p)) for p in zip(highlight_path, highlight_path[1:])}

    # all roads
    for a, b, w in EDGES:
        (x1, y1), (x2, y2) = POSITIONS[a], POSITIONS[b]
        ax.plot([x1, x2], [y1, y2], color="#C9CED6", lw=1.4, zorder=1)
        if show_all_distances and tuple(sorted((a, b))) not in route_edges:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2, km(w), fontsize=7, color="#6B7280",
                    ha="center", va="center", zorder=2,
                    bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none"))

    # the route
    for a, b in zip(highlight_path, highlight_path[1:]):
        (x1, y1), (x2, y2) = POSITIONS[a], POSITIONS[b]
        ax.plot([x1, x2], [y1, y2], color="#E4572E", lw=4, zorder=3, solid_capstyle="round")
        w = next(wt for v, wt in graph[a] if v == b)
        ax.text((x1 + x2) / 2, (y1 + y2) / 2, km(w), fontsize=8, fontweight="bold",
                color="#B23A18", ha="center", va="center", zorder=6,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="#E4572E", lw=0.8))

    # places
    for n, (x, y) in POSITIONS.items():
        if n == source:
            color = "#2E9E5B"
        elif n == target:
            color = "#D62839"
        elif n in on_path:
            color = "#F4A261"
        else:
            color = "#3B6EA8"
        ax.scatter(x, y, s=150, color=color, zorder=4, edgecolors="white", linewidths=1.8)
        (dx, dy), ha, va = OFFSETS[LABEL_POS.get(n, "below")]
        ax.annotate(n, (x, y), xytext=(dx, dy), textcoords="offset points", ha=ha, va=va,
                    fontsize=8.5, fontweight="bold" if n in on_path else "normal",
                    color="#111827", zorder=5, path_effects=OUTLINE)

    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.margins(0.12)
    fig.tight_layout()
    return fig


# ----------------------------------------------------------- map + step table
left, right = st.columns([5, 4])

with left:
    st.subheader("Route on the map")
    show_all = st.checkbox("Show distance (km) on every road", value=False)
    st.pyplot(draw_map(path, show_all))
    st.caption(
        "🟢 start · 🔴 destination · 🟠 stops on the route · labels are road distances in km "
        f"(estimated: straight-line × {CIRCUITY}). North is up."
    )

with right:
    st.subheader("How Dijkstra got there")
    st.caption(
        "Each row is one place 'finalised' (popped from the min-heap with the smallest "
        "known distance). 'Relaxed' lists neighbours whose distance improved."
    )
    rows = []
    for s in steps:
        rows.append(
            {
                "Step": s["step"],
                "Place finalised": s["visited_node"],
                "Dist (km)": km(s["distance"]),
                "Relaxed neighbours (km)": ", ".join(f"{v} ({km(d)})" for v, d in s["relaxed"]) or "—",
            }
        )
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=520)

    with st.expander("Distance table after each step"):
        snap_rows = []
        for s in steps:
            row = {"Step": s["step"], "Finalised": s["visited_node"]}
            for n in places:
                d = s["snapshot"][n]
                row[n] = "∞" if d == float("inf") else km(d)
            snap_rows.append(row)
        st.dataframe(pd.DataFrame(snap_rows), hide_index=True, width="stretch")

# ------------------------------------------------------- BFS vs Dijkstra
st.subheader("Why Dijkstra? Comparison with BFS")
bfs = bfs_path(graph, source, target)
bfs_dist = path_weight(graph, bfs)

cA, cB = st.columns(2)
with cA:
    st.markdown("**Dijkstra** (uses distances)")
    st.write("  →  ".join(path))
    st.write(f"{km(total)} km · {len(path) - 1} road segments")
with cB:
    st.markdown("**BFS** (counts road segments only, ignores distances)")
    st.write("  →  ".join(bfs))
    st.write(f"{km(bfs_dist)} km · {len(bfs) - 1} road segments")

if bfs_dist > total:
    st.warning(
        f"BFS picked the route with the fewest road segments, but it is {km(bfs_dist - total)} km longer. "
        "BFS only gives the true shortest path when every road has the same length."
    )
else:
    st.info(
        "For this pair both give the same route. Try other pairs "
        "(e.g. CHRIST University → Whitefield, or Majestic → Whitefield) to see BFS go wrong."
    )

# ---------------------------------------------------------------- complexity
with st.expander("Algorithm & complexity"):
    st.markdown(
        f"""
- **Idea (greedy):** always finalise the unvisited place with the smallest known distance; its distance can never improve later (valid because no road length is negative).
- **Data structure:** binary min-heap (`heapq`) with lazy deletion of stale entries.
- **Time:** O((V + E) log V) · **Space:** O(V + E). Here V = {len(places)} places, E = {len(EDGES)} roads.
- **Limitation:** fails with negative edge weights (use Bellman-Ford there).
- **Data note:** place coordinates are real (approximate); road distances are estimated as straight-line distance × {CIRCUITY}, not surveyed.
        """
    )

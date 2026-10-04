"""
Map data for the prototype: Bengaluru.

LANDMARKS : real places with approximate GPS coordinates (latitude, longitude).
ROADS     : which landmarks are directly connected by a main road
            (arterial roads such as Hosur Road, Outer Ring Road, Old Airport
            Road, Mysore Road, Tumkur Road, ...).

Edge weights are ROAD DISTANCES ESTIMATED from the coordinates:
    straight-line (haversine) distance x CIRCUITY
A circuity factor of ~1.3 is a common rule of thumb for how much longer city
roads are than a straight line. So distances are approximate, not surveyed.
To use exact numbers, replace the computed weight for any road with a
measured value (see WEIGHT_OVERRIDES below) - nothing else needs to change.

Weights are stored as integer metres (rounded to the nearest 100 m) so the
algorithm and tests use exact integer arithmetic.
"""

import math

from dijkstra import build_graph

CIRCUITY = 1.3

# name: (latitude, longitude) - approximate
LANDMARKS = {
    "Majestic": (12.9770, 77.5713),
    "Cubbon Park": (12.9763, 77.5929),
    "MG Road": (12.9756, 77.6065),
    "Ulsoor Lake": (12.9831, 77.6196),
    "Indiranagar": (12.9784, 77.6408),
    "Domlur": (12.9610, 77.6387),
    "Koramangala": (12.9352, 77.6245),
    "CHRIST University": (12.9346, 77.6063),
    "Lalbagh": (12.9507, 77.5848),
    "Jayanagar": (12.9308, 77.5838),
    "Basavanagudi": (12.9422, 77.5737),
    "Banashankari": (12.9255, 77.5468),
    "JP Nagar": (12.9063, 77.5857),
    "BTM Layout": (12.9166, 77.6101),
    "Silk Board": (12.9177, 77.6228),
    "HSR Layout": (12.9116, 77.6474),
    "Bellandur": (12.9304, 77.6784),
    "Marathahalli": (12.9569, 77.7011),
    "Whitefield": (12.9698, 77.7500),
    "KR Puram": (13.0035, 77.6960),
    "Electronic City": (12.8452, 77.6602),
    "Hebbal": (13.0358, 77.5970),
    "Yeshwanthpur": (13.0285, 77.5400),
    "Rajajinagar": (12.9916, 77.5550),
    "Malleshwaram": (13.0035, 77.5710),
}

# Direct road connections (two-way)
ROADS = [
    # Central Bengaluru
    ("Majestic", "Cubbon Park"),
    ("Cubbon Park", "MG Road"),
    ("MG Road", "Ulsoor Lake"),
    ("Ulsoor Lake", "Indiranagar"),
    ("MG Road", "Indiranagar"),
    ("MG Road", "CHRIST University"),
    ("Cubbon Park", "Hebbal"),
    # West / north-west
    ("Majestic", "Malleshwaram"),
    ("Majestic", "Rajajinagar"),
    ("Rajajinagar", "Malleshwaram"),
    ("Rajajinagar", "Yeshwanthpur"),
    ("Malleshwaram", "Yeshwanthpur"),
    ("Malleshwaram", "Hebbal"),
    ("Hebbal", "Yeshwanthpur"),
    # South
    ("Majestic", "Lalbagh"),
    ("Majestic", "Basavanagudi"),
    ("Lalbagh", "Basavanagudi"),
    ("Lalbagh", "Jayanagar"),
    ("Lalbagh", "CHRIST University"),
    ("Basavanagudi", "Banashankari"),
    ("Jayanagar", "Banashankari"),
    ("Jayanagar", "JP Nagar"),
    ("Jayanagar", "BTM Layout"),
    ("JP Nagar", "Banashankari"),
    ("JP Nagar", "BTM Layout"),
    # South-east (Hosur Road / Outer Ring Road corridor)
    ("CHRIST University", "Koramangala"),
    ("CHRIST University", "Silk Board"),
    ("Koramangala", "Silk Board"),
    ("Koramangala", "BTM Layout"),
    ("BTM Layout", "Silk Board"),
    ("BTM Layout", "HSR Layout"),
    ("Silk Board", "HSR Layout"),
    ("Silk Board", "Electronic City"),
    ("HSR Layout", "Bellandur"),
    ("Koramangala", "Domlur"),
    # East
    ("Indiranagar", "Domlur"),
    ("Domlur", "Marathahalli"),
    ("Bellandur", "Marathahalli"),
    ("Marathahalli", "Whitefield"),
    ("Marathahalli", "KR Puram"),
    ("KR Puram", "Whitefield"),
    ("Indiranagar", "KR Puram"),
    ("KR Puram", "Hebbal"),
]

# Optional: put exact measured distances (in metres) here to override the estimate,
# e.g. {("Majestic", "Cubbon Park"): 3200}
WEIGHT_OVERRIDES = {}


def haversine_m(a, b):
    """Great-circle (straight-line) distance in metres between two (lat, lon) points."""
    r = 6371000.0
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 2 * r * math.asin(math.sqrt(h))


def _weight(a, b):
    if (a, b) in WEIGHT_OVERRIDES:
        return WEIGHT_OVERRIDES[(a, b)]
    if (b, a) in WEIGHT_OVERRIDES:
        return WEIGHT_OVERRIDES[(b, a)]
    est = haversine_m(LANDMARKS[a], LANDMARKS[b]) * CIRCUITY
    return int(round(est / 100.0)) * 100          # nearest 100 m


NODES = list(LANDMARKS.keys())
EDGES = [(a, b, _weight(a, b)) for a, b in ROADS]

# (x, y) for drawing: longitude scaled by cos(latitude) so the map is not stretched
_LAT0 = sum(lat for lat, _ in LANDMARKS.values()) / len(LANDMARKS)
POSITIONS = {
    name: (lon * math.cos(math.radians(_LAT0)), lat)
    for name, (lat, lon) in LANDMARKS.items()
}


def load_graph():
    return build_graph(NODES, EDGES)

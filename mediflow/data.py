"""Fictional city map and default scenario for MediFlow."""
import copy
import math

# Every map unit of distance costs this many minutes on an empty road.
COST_PER_UNIT = 3.0

# Intersections and hospitals: name -> (x, y) position on the simulated map.
NODES = {
    "Central": (5, 5), "Old Town": (3, 5), "Market": (7, 5),
    "North Park": (5, 8), "Riverside": (2, 8), "Tech Hub": (8, 8),
    "South Gate": (5, 2), "Harbor": (2, 2), "Airport Rd": (8, 2),
    "City General": (1, 5), "East Clinic": (9, 5), "North Med": (5, 10),
}

HOSPITAL_NODES = ["City General", "East Clinic", "North Med"]

# Roads connect two nodes. Their base cost is the straight-line distance
# times COST_PER_UNIT (minutes).
ROADS = [
    ("Central", "Old Town"), ("Central", "Market"),
    ("Central", "North Park"), ("Central", "South Gate"),
    ("Old Town", "Riverside"), ("Old Town", "Harbor"),
    ("Old Town", "City General"), ("Market", "Tech Hub"),
    ("Market", "Airport Rd"), ("Market", "East Clinic"),
    ("North Park", "Riverside"), ("North Park", "Tech Hub"),
    ("North Park", "North Med"), ("South Gate", "Harbor"),
    ("South Gate", "Airport Rd"), ("Riverside", "City General"),
    ("Tech Hub", "East Clinic"), ("Harbor", "City General"),
]

NEEDS = ["Basic", "ICU", "Trauma"]          # patient requirements
STATUSES = ["Open", "Dispatched", "Resolved"]


def edge_key(a, b):
    """A road has no direction, so we store it as a sorted pair."""
    return tuple(sorted((a, b)))


def distance(a, b):
    (x1, y1), (x2, y2) = NODES[a], NODES[b]
    return math.hypot(x1 - x2, y1 - y2)


def base_cost(a, b):
    """Travel time (minutes) of a road with no traffic."""
    return distance(a, b) * COST_PER_UNIT


def default_scenario():
    """Return a fresh copy of the starting scenario."""
    return copy.deepcopy({
        "traffic": {},      # edge_key -> multiplier (1.0 = no traffic)
        "blocked": [],      # list of edge_keys that are closed
        "hospitals": [
            {"name": "City General", "services": ["Basic", "ICU", "Trauma"],
             "total_beds": 10, "occupied": 6},
            {"name": "East Clinic", "services": ["Basic", "ICU"],
             "total_beds": 6, "occupied": 3},
            {"name": "North Med", "services": ["Basic", "Trauma"],
             "total_beds": 8, "occupied": 7},
        ],
        "ambulances": [
            {"id": "AMB-1", "base": "Central", "equipment": ["Basic"], "status": "Available"},
            {"id": "AMB-2", "base": "South Gate", "equipment": ["Basic", "ICU"], "status": "Available"},
            {"id": "AMB-3", "base": "Tech Hub", "equipment": ["Basic", "Trauma"], "status": "Available"},
            {"id": "AMB-4", "base": "Harbor", "equipment": ["Basic", "ICU", "Trauma"], "status": "Available"},
            {"id": "AMB-5", "base": "Airport Rd", "equipment": ["Basic"], "status": "Available"},
        ],
        "incidents": [
            {"id": "INC-0", "location": "Old Town", "severity": 2, "need": "Basic",
             "status": "Resolved", "desc": "Minor fall (earlier today)", "amb": "AMB-1", "hospital": "City General"},
            {"id": "INC-1", "location": "Riverside", "severity": 5, "need": "ICU",
             "status": "Open", "desc": "Cardiac arrest", "amb": "", "hospital": ""},
            {"id": "INC-2", "location": "Market", "severity": 3, "need": "Basic",
             "status": "Open", "desc": "Broken arm", "amb": "", "hospital": ""},
            {"id": "INC-3", "location": "Harbor", "severity": 4, "need": "Trauma",
             "status": "Open", "desc": "Dock accident", "amb": "", "hospital": ""},
            {"id": "INC-4", "location": "Airport Rd", "severity": 2, "need": "Basic",
             "status": "Open", "desc": "Fainting at terminal", "amb": "", "hospital": ""},
            {"id": "INC-5", "location": "Tech Hub", "severity": 5, "need": "Trauma",
             "status": "Open", "desc": "Multi-vehicle crash", "amb": "", "hospital": ""},
        ],
        "log": ["Default scenario loaded"],
    })

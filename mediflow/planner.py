"""Glue code: runs the whole workflow
incident registration -> route planning (A*) -> CSP allocation -> Minimax / Alpha-Beta."""
from mediflow.routing import build_adjacency, travel_tables
from mediflow.csp import allocate
from mediflow.strategy import build_world, minimax_decide, alphabeta_decide


def free_beds(hospital):
    return max(0, hospital["total_beds"] - hospital["occupied"])


def prepare(sc):
    """Read the scenario and compute everything the algorithms need."""
    adj = build_adjacency(sc["traffic"], sc["blocked"])
    incidents = [i for i in sc["incidents"] if i["status"] == "Open"]
    ambulances = [a for a in sc["ambulances"] if a["status"] == "Available"]
    hospitals = [dict(h, free=free_beds(h)) for h in sc["hospitals"]]
    amb_inc, inc_hosp = travel_tables(adj, incidents, ambulances, hospitals)
    return {"adj": adj, "incidents": incidents, "ambulances": ambulances, "hospitals": hospitals,
            "amb_inc": amb_inc, "inc_hosp": inc_hosp}


def plan(sc):
    """Steps 1-3: routes and CSP allocation."""
    prep = prepare(sc)
    alloc = allocate(prep["incidents"], prep["ambulances"], prep["hospitals"],
                     prep["amb_inc"], prep["inc_hosp"])
    return prep, alloc


def make_world(prep):
    return build_world(prep["incidents"], prep["ambulances"], prep["hospitals"],
                       prep["amb_inc"], prep["inc_hosp"])


def run_workflow(sc, depth=3):
    """Full pipeline, used by the tests and the evaluation page."""
    prep, alloc = plan(sc)
    world = make_world(prep)
    depth = max(1, min(depth, len(world["incidents"]))) if world["incidents"] else 0
    return {"prep": prep, "alloc": alloc, "world": world, "depth": depth,
            "minimax": minimax_decide(world, depth), "alphabeta": alphabeta_decide(world, depth)}

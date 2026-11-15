"""Minimax and Alpha-Beta pruning for choosing a dispatch plan.

Game description
  MAX (dispatcher): picks the next open incident to dispatch. The nearest
                    compatible free ambulance and a compatible hospital with a
                    free bed are used automatically.
  MIN (adversary) : after each dispatch, picks the worst event for us:
                      - Heavy traffic            : response time x 1.5
                      - Hospital overload        : the hospital loses one extra bed
                      - Ambulance out of service : the most capable free ambulance is lost
  Transition      : the incident is removed, the ambulance and a bed are used.
  Terminal state  : search depth reached, no incidents left, or no free ambulance.
  Utility (higher is better)
      + severity * (20 - 0.5 * response_minutes)   patient served (faster = better)
      - severity * 15                              patient never served
      - 5                                          hospital left with 0 free beds
"""
import time

INF = float("inf")
UNSERVED_PENALTY = 15
OVERLOAD_PENALTY = 5
ADVERSE = ["Heavy traffic", "Hospital overload", "Ambulance out of service"]


def build_world(incidents, ambulances, hospitals, amb_inc, inc_hosp):
    """Collect the fixed facts of the scenario in one dictionary."""
    ordered = sorted(incidents, key=lambda i: (-i["severity"], i["id"]))
    return {
        "incidents": [i["id"] for i in ordered],            # most severe first
        "severity": {i["id"]: i["severity"] for i in incidents},
        "need": {i["id"]: i["need"] for i in incidents},
        "ambs": [a["id"] for a in ambulances],
        "equip": {a["id"]: a["equipment"] for a in ambulances},
        "services": {h["name"]: h["services"] for h in hospitals},
        "beds": {h["name"]: h["free"] for h in hospitals},
        "amb_inc": amb_inc,
        "inc_hosp": inc_hosp,
    }


class State:
    """What is still left to do: open incidents, free ambulances, free beds, score."""

    def __init__(self, remaining, free, beds, score=0.0):
        self.remaining, self.free, self.beds, self.score = remaining, free, beds, score

    def copy(self):
        return State(list(self.remaining), list(self.free), dict(self.beds), self.score)


def start_state(world):
    return State(list(world["incidents"]), list(world["ambs"]), dict(world["beds"]))


def find_trip(world, state, inc):
    """Nearest compatible free ambulance + nearest compatible hospital with a bed.
    Returns None if the incident cannot be served right now."""
    need = world["need"][inc]
    best_amb = None
    for a in state.free:
        t = world["amb_inc"][(a, inc)]
        if need in world["equip"][a] and t < INF and (best_amb is None or t < best_amb[1]):
            best_amb = (a, t)
    best_hosp = None
    for h, beds in state.beds.items():
        t = world["inc_hosp"][(inc, h)]
        if beds > 0 and need in world["services"][h] and t < INF and (best_hosp is None or t < best_hosp[1]):
            best_hosp = (h, t)
    if best_amb is None or best_hosp is None:
        return None
    return {"incident": inc, "amb": best_amb[0], "response": best_amb[1],
            "hospital": best_hosp[0], "to_hospital": best_hosp[1]}


def after_max(world, state, inc):
    """MAX moves: dispatch (or fail to serve) one incident."""
    new = state.copy()
    new.remaining.remove(inc)
    trip = find_trip(world, state, inc)
    if trip is None:                                   # nobody can serve it
        new.score -= world["severity"][inc] * UNSERVED_PENALTY
        return new, None
    new.free.remove(trip["amb"])
    new.beds[trip["hospital"]] -= 1
    return new, trip


def after_min(world, state, trip, adverse):
    """MIN moves: apply one adverse event and score the dispatch."""
    new = state.copy()
    response, hosp = trip["response"], trip["hospital"]
    if adverse == "Heavy traffic":
        response *= 1.5
    elif adverse == "Hospital overload":
        new.beds[hosp] = max(0, new.beds[hosp] - 1)
    elif adverse == "Ambulance out of service" and new.free:
        new.free.remove(max(new.free, key=lambda a: len(world["equip"][a])))
    new.score += world["severity"][trip["incident"]] * (20 - 0.5 * response)
    if new.beds[hosp] == 0:
        new.score -= OVERLOAD_PENALTY
    return new


def is_terminal(state, depth):
    return depth == 0 or not state.remaining or not state.free


def final_value(world, state):
    """Utility of a finished plan: score minus penalty for anyone left unserved."""
    return state.score - sum(world["severity"][i] * UNSERVED_PENALTY for i in state.remaining)


# ---------------------------------------------------------------- Minimax
def max_node(world, state, depth, stats):
    stats["nodes"] += 1
    if is_terminal(state, depth):
        return final_value(world, state)
    value = -INF
    for inc in list(state.remaining):
        new, trip = after_max(world, state, inc)
        if trip is None:
            child = max_node(world, new, depth - 1, stats)
        else:
            child = min_node(world, new, trip, depth - 1, stats)
        value = max(value, child)
    return value


def min_node(world, state, trip, depth, stats):
    stats["nodes"] += 1
    value = INF
    for adverse in ADVERSE:
        child = max_node(world, after_min(world, state, trip, adverse), depth, stats)
        value = min(value, child)
    return value


def minimax_decide(world, depth):
    """Evaluate every first dispatch and pick the best worst-case utility."""
    t0 = time.perf_counter()
    state, stats = start_state(world), {"nodes": 1, "pruned": 0}
    if is_terminal(state, depth):
        return {"action": None, "utility": final_value(world, state), "values": {}, "nodes": 1,
                "pruned": 0, "time_ms": 0.0}
    values, per_plan, best_action, best_value = {}, {}, None, -INF
    for inc in list(state.remaining):
        before = stats["nodes"]
        new, trip = after_max(world, state, inc)
        if trip is None:
            v = max_node(world, new, depth - 1, stats)
        else:
            v = min_node(world, new, trip, depth - 1, stats)
        values[inc] = v
        per_plan[inc] = stats["nodes"] - before
        if v > best_value:
            best_action, best_value = inc, v
    return {"action": best_action, "utility": best_value, "values": values, "per_plan": per_plan, "nodes": stats["nodes"],
            "pruned": 0, "time_ms": (time.perf_counter() - t0) * 1000}


# ------------------------------------------------------------- Alpha-Beta
def ab_max(world, state, depth, alpha, beta, stats):
    stats["nodes"] += 1
    if is_terminal(state, depth):
        return final_value(world, state)
    value = -INF
    for inc in list(state.remaining):
        new, trip = after_max(world, state, inc)
        if trip is None:
            child = ab_max(world, new, depth - 1, alpha, beta, stats)
        else:
            child = ab_min(world, new, trip, depth - 1, alpha, beta, stats)
        value = max(value, child)
        alpha = max(alpha, value)
        if alpha >= beta:                  # MIN above will never allow this branch
            stats["pruned"] += 1
            break
    return value


def ab_min(world, state, trip, depth, alpha, beta, stats):
    stats["nodes"] += 1
    value = INF
    for adverse in ADVERSE:
        child = ab_max(world, after_min(world, state, trip, adverse), depth, alpha, beta, stats)
        value = min(value, child)
        beta = min(beta, value)
        if alpha >= beta:                  # MAX above already has something better
            stats["pruned"] += 1
            break
    return value


def alphabeta_decide(world, depth):
    """Same decision as minimax_decide, but skips branches that cannot matter."""
    t0 = time.perf_counter()
    state, stats = start_state(world), {"nodes": 1, "pruned": 0}
    if is_terminal(state, depth):
        return {"action": None, "utility": final_value(world, state), "nodes": 1, "pruned": 0, "time_ms": 0.0}
    per_plan, best_action, best_value = {}, None, -INF
    for inc in list(state.remaining):
        before = stats["nodes"]
        new, trip = after_max(world, state, inc)
        if trip is None:
            v = ab_max(world, new, depth - 1, best_value, INF, stats)
        else:
            v = ab_min(world, new, trip, depth - 1, best_value, INF, stats)
        per_plan[inc] = stats["nodes"] - before
        if v > best_value:
            best_action, best_value = inc, v
    return {"action": best_action, "utility": best_value, "per_plan": per_plan, "nodes": stats["nodes"],
            "pruned": stats["pruned"], "time_ms": (time.perf_counter() - t0) * 1000}


def adverse_breakdown(world, depth, inc):
    """For one first dispatch, show the utility under each adverse event."""
    state = start_state(world)
    new, trip = after_max(world, state, inc)
    if trip is None:
        return {}
    return {adv: max_node(world, after_min(world, new, trip, adv), depth - 1, {"nodes": 0})
            for adv in ADVERSE}


# ------------------------------------------------- decision tree recorder
def decision_tree(world, depth, alphabeta):
    """Record the top of the real search tree for the GUI.

    Level 1 = MAX's first dispatch, level 2 = MIN's adverse reply. It runs the
    same loops as minimax_decide / alphabeta_decide (so node counts and values
    match them exactly); the deeper subtrees below each reply are searched by
    the normal max_node / ab_max functions and summarised as a value + node count.
    With alphabeta=True, replies that Alpha-Beta never evaluates are marked
    pruned (value None), and a plan that was cut off holds only an upper bound.
    """
    state, stats = start_state(world), {"nodes": 1, "pruned": 0}
    seq = [0]                                   # order in which nodes are evaluated

    def tick():
        seq[0] += 1
        return seq[0]

    plans, best_value, best_action = [], -INF, None
    for inc in list(state.remaining):
        before = stats["nodes"]
        new, trip = after_max(world, state, inc)
        plan = {"inc": inc, "trip": trip, "children": [], "seq": tick(), "cut": False}
        if trip is None:                        # nobody can serve it: no MIN node
            if alphabeta:
                plan["value"] = ab_max(world, new, depth - 1, best_value, INF, stats)
            else:
                plan["value"] = max_node(world, new, depth - 1, stats)
        else:
            stats["nodes"] += 1                 # the MIN node
            alpha, beta, value = (best_value if alphabeta else -INF), INF, INF
            for k, adverse in enumerate(ADVERSE):
                n0 = stats["nodes"]
                child_state = after_min(world, new, trip, adverse)
                if alphabeta:
                    child = ab_max(world, child_state, depth - 1, alpha, beta, stats)
                else:
                    child = max_node(world, child_state, depth - 1, stats)
                plan["children"].append({"name": adverse, "value": child, "pruned": False, "seq": tick(),
                                         "nodes": stats["nodes"] - n0, "terminal": is_terminal(child_state, depth - 1)})
                value = min(value, child)
                if alphabeta:
                    beta = min(beta, value)
                    if alpha >= beta:           # remaining replies are never evaluated
                        stats["pruned"] += 1
                        plan["cut"] = True
                        for rest in ADVERSE[k + 1:]:
                            plan["children"].append({"name": rest, "value": None, "pruned": True,
                                                     "seq": tick(), "nodes": 0, "terminal": False})
                        break
            plan["value"] = value
        plan["nodes"] = stats["nodes"] - before
        if plan["value"] > best_value:
            best_action, best_value = inc, plan["value"]
        plans.append(plan)
    for plan in plans:
        live = [c for c in plan["children"] if not c["pruned"]]
        plan["worst"] = next((c["name"] for c in live if abs(c["value"] - plan["value"]) < 1e-9), None) \
            if plan["children"] else None
        plan["chosen"] = plan["inc"] == best_action
    return {"algo": "Alpha-Beta" if alphabeta else "Minimax", "plans": plans, "action": best_action,
            "utility": best_value, "nodes": stats["nodes"], "pruned": stats["pruned"], "depth": depth}

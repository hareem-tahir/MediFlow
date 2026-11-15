"""Road network helpers plus the two route-finding algorithms: Dijkstra and A*."""
import heapq
import time

from mediflow.data import NODES, ROADS, COST_PER_UNIT, edge_key, distance, base_cost

INF = float("inf")


def build_adjacency(traffic, blocked):
    """Turn the scenario's roads into {node: [(neighbour, cost), ...]}.
    Blocked roads are left out. Traffic multiplies the cost (never below 1.0,
    which keeps the A* heuristic admissible)."""
    adj = {node: [] for node in NODES}
    for a, b in ROADS:
        key = edge_key(a, b)
        if key in blocked:
            continue
        cost = base_cost(a, b) * max(1.0, traffic.get(key, 1.0))
        adj[a].append((b, cost))
        adj[b].append((a, cost))
    return adj


def heuristic(node, goal):
    """Straight-line travel time. It never overestimates the real cost
    because every road costs at least its straight-line distance."""
    return distance(node, goal) * COST_PER_UNIT


def _make_route(prev, start, goal):
    route = [goal]
    while route[-1] != start:
        route.append(prev[route[-1]])
    return route[::-1]


def _search(adj, start, goal, use_heuristic, trace=False):
    """Shared best-first search. Dijkstra orders the queue by cost so far (g);
    A* orders it by g + heuristic. With trace=True every expansion is recorded
    (used by the step-through visualisation; it does not change the result)."""
    h = (lambda n: heuristic(n, goal)) if use_heuristic else (lambda n: 0.0)
    best = {start: 0.0}          # cheapest known cost to each node
    prev = {}                    # where we came from
    done = set()                 # nodes already expanded
    queue = [(h(start), 0.0, start)]                  # (f, g, node)
    order, steps = [], []        # expansion order / optional trace
    result = {"route": [], "cost": INF}
    while queue:
        _, g, node = heapq.heappop(queue)
        if node in done:
            continue
        done.add(node)
        order.append(node)
        relaxed, edges = [], []
        if node == goal:
            result = {"route": _make_route(prev, start, goal), "cost": g}
        else:
            for nxt, w in adj[node]:
                new_g = g + w
                old_g = best.get(nxt)                      # cheapest cost known before this look
                if trace:                                  # what happened on this road (for the GUI)
                    status = ("new" if old_g is None else "better" if new_g < old_g
                              else "closed" if nxt in done else "worse")
                    edges.append({"to": nxt, "w": w, "new_g": new_g, "old_g": old_g, "h": h(nxt), "status": status})
                if new_g < best.get(nxt, INF):
                    best[nxt] = new_g
                    prev[nxt] = node
                    relaxed.append(nxt)
                    heapq.heappush(queue, (new_g + h(nxt), new_g, nxt))
        if trace:
            frontier = sorted({n: (best[n], best[n] + h(n)) for _, _, n in queue if n not in done}.items(),
                              key=lambda kv: kv[1][1])
            steps.append({"node": node, "g": g, "h": h(node), "f": g + h(node), "relaxed": relaxed, "edges": edges,
                          "frontier": [{"node": n, "g": gg, "f": ff} for n, (gg, ff) in frontier]})
        if node == goal:
            break
    result.update(explored=len(order), order=order)
    if trace:
        result["trace"] = steps
    return result


def dijkstra(adj, start, goal, trace=False):
    """Always expand the cheapest node found so far."""
    return _search(adj, start, goal, False, trace)


def astar(adj, start, goal, trace=False):
    """Like Dijkstra, but nodes are ordered by cost-so-far + heuristic,
    so the search leans toward the goal."""
    return _search(adj, start, goal, True, trace)


def alternative_routes(adj, start, goal, k=2):
    """Next-best routes: close each road of the best route in turn, re-run A*,
    and keep the cheapest distinct detours. Returns [{route, cost, extra}]."""
    best = astar(adj, start, goal)
    if not best["route"]:
        return []
    found = {}
    for a, b in zip(best["route"], best["route"][1:]):
        reduced = {n: [(m, w) for m, w in nbrs if {n, m} != {a, b}] for n, nbrs in adj.items()}
        alt = astar(reduced, start, goal)
        if alt["route"] and alt["route"] != best["route"]:
            found[tuple(alt["route"])] = alt["cost"]
    ranked = sorted(found.items(), key=lambda kv: kv[1])[:k]
    return [{"route": list(r), "cost": c, "extra": c - best["cost"]} for r, c in ranked]


def _timed(func, adj, start, goal, repeats):
    """Run a search several times and report the average time in ms."""
    t0 = time.perf_counter()
    for _ in range(repeats):
        result = func(adj, start, goal)
    result = dict(result)
    result["time_ms"] = (time.perf_counter() - t0) * 1000 / repeats
    return result


def compare(adj, start, goal, repeats=100):
    """Run A* and Dijkstra on the same graph and the same trip."""
    return _timed(astar, adj, start, goal, repeats), _timed(dijkstra, adj, start, goal, repeats)


def unreachable_nodes(adj):
    """Nodes that cannot be reached from 'Central' (e.g. after road closures)."""
    seen, stack = {"Central"}, ["Central"]
    while stack:
        for nxt, _ in adj[stack.pop()]:
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return [n for n in NODES if n not in seen]


def travel_tables(adj, incidents, ambulances, hospitals):
    """Pre-compute travel times with A* for the CSP and the strategy search.
    amb_inc[(ambulance_id, incident_id)] and inc_hosp[(incident_id, hospital)]."""
    amb_inc, inc_hosp = {}, {}
    for inc in incidents:
        for a in ambulances:
            amb_inc[(a["id"], inc["id"])] = astar(adj, a["base"], inc["location"])["cost"]
        for h in hospitals:
            inc_hosp[(inc["id"], h["name"])] = astar(adj, inc["location"], h["name"])["cost"]
    return amb_inc, inc_hosp

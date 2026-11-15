"""Tests for A* and Dijkstra."""
from mediflow.data import NODES, ROADS, edge_key, default_scenario
from mediflow.routing import build_adjacency, astar, dijkstra, heuristic, compare, unreachable_nodes, INF


def test_same_cost_for_every_pair():
    adj = build_adjacency({}, [])
    for a in NODES:
        for b in NODES:
            assert abs(astar(adj, a, b)["cost"] - dijkstra(adj, a, b)["cost"]) < 1e-9


def test_same_cost_with_traffic_and_closures():
    traffic = {edge_key("Central", "Market"): 3.0, edge_key("Old Town", "Harbor"): 2.5}
    blocked = [edge_key("Central", "North Park"), edge_key("South Gate", "Harbor")]
    adj = build_adjacency(traffic, blocked)
    for a in NODES:
        for b in NODES:
            assert abs(astar(adj, a, b)["cost"] - dijkstra(adj, a, b)["cost"]) < 1e-9


def test_heuristic_is_admissible():
    adj = build_adjacency({edge_key("Central", "Old Town"): 4.0}, [])
    for a in NODES:
        for b in NODES:
            assert heuristic(a, b) <= dijkstra(adj, a, b)["cost"] + 1e-9


def test_blocked_road_changes_route():
    open_adj = build_adjacency({}, [])
    shut_adj = build_adjacency({}, [edge_key("Central", "Old Town")])
    before = astar(open_adj, "Central", "Old Town")
    after = astar(shut_adj, "Central", "Old Town")
    assert before["route"] == ["Central", "Old Town"]
    assert len(after["route"]) > 2 and after["cost"] > before["cost"]


def test_traffic_raises_cost():
    free = astar(build_adjacency({}, []), "Central", "Market")["cost"]
    jam = astar(build_adjacency({edge_key("Central", "Market"): 3.0}, []), "Central", "Market")["cost"]
    assert jam > free


def test_unreachable_goal():
    blocked = [edge_key(a, b) for a, b in ROADS if "North Med" in (a, b)]
    adj = build_adjacency({}, blocked)
    for algo in (astar, dijkstra):
        result = algo(adj, "Central", "North Med")
        assert result["route"] == [] and result["cost"] == INF
    assert unreachable_nodes(adj) == ["North Med"]


def test_start_equals_goal():
    adj = build_adjacency({}, [])
    for algo in (astar, dijkstra):
        result = algo(adj, "Harbor", "Harbor")
        assert result["route"] == ["Harbor"] and result["cost"] == 0 and result["explored"] == 1


def test_astar_never_explores_more_on_open_map_than_all_nodes():
    adj = build_adjacency({}, [])
    a, d = compare(adj, "Harbor", "North Med", repeats=3)
    assert a["explored"] <= d["explored"] and a["time_ms"] >= 0

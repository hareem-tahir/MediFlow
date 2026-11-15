"""Tests for the new visual layer: search traces, alternative routes, decision-tree recorder, HTML views."""
from mediflow import cityview as cv
from mediflow.data import default_scenario, edge_key
from mediflow.planner import plan, make_world, run_workflow
from mediflow.routing import astar, dijkstra, alternative_routes, build_adjacency
from mediflow.strategy import decision_tree


def test_trace_matches_result():
    adj = build_adjacency({}, [])
    for fn in (astar, dijkstra):
        r = fn(adj, "Harbor", "North Med", trace=True)
        assert [s["node"] for s in r["trace"]] == r["order"] and len(r["trace"]) == r["explored"]
        assert abs(r["trace"][-1]["g"] - r["cost"]) < 1e-9
        assert r["cost"] == fn(adj, "Harbor", "North Med")["cost"]      # tracing does not change the answer


def test_alternatives_are_valid_and_not_cheaper():
    adj = build_adjacency({}, [])
    best = astar(adj, "Harbor", "North Med")
    alts = alternative_routes(adj, "Harbor", "North Med", 2)
    assert alts and all(a["route"] != best["route"] and a["cost"] >= best["cost"] - 1e-9 for a in alts)


def test_decision_tree_equals_real_algorithms():
    for depth in (1, 2, 3):
        r = run_workflow(default_scenario(), depth)
        mm, ab = decision_tree(r["world"], depth, False), decision_tree(r["world"], depth, True)
        assert mm["nodes"] == r["minimax"]["nodes"] and ab["nodes"] == r["alphabeta"]["nodes"]
        assert ab["pruned"] == r["alphabeta"]["pruned"]
        assert mm["action"] == r["minimax"]["action"] == ab["action"]
        assert abs(mm["utility"] - r["minimax"]["utility"]) < 1e-9


def test_html_views_build():
    sc = default_scenario()
    sc["blocked"].append(edge_key("Central", "Market"))
    prep, alloc = plan(sc)
    ms = cv.build_missions(prep["adj"], sc, [(i, v[0], v[1]) for i, v in alloc["assignments"].items()], "planned")
    assert len(ms) == len(alloc["assignments"]) and all(m["total"] > m["scene_time"] >= 0 for m in ms)
    assert "Run dispatch" in cv.dispatch_map_html(sc, prep["adj"], ms)
    a, d = astar(prep["adj"], "Harbor", "North Med", trace=True), dijkstra(prep["adj"], "Harbor", "North Med", trace=True)
    assert "Play search" in cv.search_html(sc, "Harbor", "North Med", a, d)
    w = make_world(prep)
    assert "Replay" in cv.tree_html(decision_tree(w, 2, False), decision_tree(w, 2, True))
    assert "cc good" in cv.csp_cards_html(prep, alloc)


def test_search_trace_records_every_road_with_its_weight():
    adj = build_adjacency({edge_key("Old Town", "Harbor"): 2.0}, [])
    r = astar(adj, "Harbor", "North Med", trace=True)
    first = r["trace"][0]
    assert first["node"] == "Harbor" and abs(first["f"] - (first["g"] + first["h"])) < 1e-9
    assert {e["to"] for e in first["edges"]} == {n for n, _ in adj["Harbor"]}
    for step in r["trace"]:
        for e in step["edges"]:
            assert abs(e["new_g"] - (step["g"] + e["w"])) < 1e-9
            assert e["status"] in ("new", "better", "worse", "closed")
            assert e["w"] == dict(adj[step["node"]])[e["to"]]


def test_search_page_carries_weights_and_h_values():
    import json, re
    sc = default_scenario()
    sc["blocked"].append(edge_key("Central", "Market"))
    prep, _ = plan(sc)
    a, d = astar(prep["adj"], "Harbor", "North Med", trace=True), dijkstra(prep["adj"], "Harbor", "North Med", trace=True)
    page = cv.search_html(sc, "Harbor", "North Med", a, d)
    data = json.loads(re.search(r"<script id='data' type='application/json'>(.*?)</script>", page, re.S).group(1))
    assert len(data["roads"]) == 17 and all(r["cost"] > 0 for r in data["roads"])    # 18 roads, 1 blocked
    astar_data = next(x for x in data["algos"] if x["key"] == "astar")
    assert astar_data["h"]["Harbor"] > 0 and astar_data["h"]["North Med"] == 0
    assert abs(sum(astar_data["legs"]) - astar_data["cost"]) < 0.1
    assert next(x for x in data["algos"] if x["key"] == "dijkstra")["h"] == {}

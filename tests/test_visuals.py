"""Tests for the animation data and figures (they must reflect the real algorithm results)."""
from mediflow.data import NODES, default_scenario, edge_key
from mediflow.planner import plan, make_world, run_workflow
from mediflow.strategy import minimax_decide
from mediflow.visuals import (make_missions, build_animation, _position, make_map, sankey_figure,
                              gantt_figure, tree_figure)


def test_missions_match_csp_times():
    prep, alloc = plan(default_scenario())
    missions = make_missions(prep, alloc)
    assert len(missions) == len(alloc["assignments"])
    for m in missions:
        amb, hosp, total, eta = alloc["assignments"][m["inc"]]
        assert abs(m["total"] - total) < 0.02 and abs(m["scene_time"] - eta) < 0.02   # CSP values are rounded
        assert _position(m, 0) == NODES[m["base"]]
        assert _position(m, m["total"] + 5) == NODES[m["hosp"]]
        assert _position(m, m["scene_time"]) == NODES[m["location"]]


def test_animation_has_frames_and_follows_traffic():
    sc = default_scenario()
    prep, alloc = plan(sc)
    fig = build_animation(sc, prep, alloc, make_missions(prep, alloc), steps=10)
    assert len(fig.frames) == 11
    base_total = max(m["total"] for m in make_missions(prep, alloc))
    for a, b in [("Central", "Old Town"), ("Central", "Market"), ("Central", "North Park"), ("Central", "South Gate")]:
        sc["traffic"][edge_key(a, b)] = 4.0
    prep2, alloc2 = plan(sc)
    assert max(m["total"] for m in make_missions(prep2, alloc2)) != base_total


def test_all_figures_build():
    sc = default_scenario()
    prep, alloc = plan(sc)
    world = make_world(prep)
    assert make_map(sc, []).data and gantt_figure(make_missions(prep, alloc)).data
    assert sankey_figure(alloc, prep["incidents"]).data
    assert tree_figure(world, 3, minimax_decide(world, 3)).data

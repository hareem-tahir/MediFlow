"""Tests for Minimax and Alpha-Beta."""
import random
from mediflow.data import default_scenario, edge_key
from mediflow.planner import prepare, make_world, run_workflow
from mediflow.strategy import (build_world, minimax_decide, alphabeta_decide, INF, UNSERVED_PENALTY)


def tiny_world(response=10, beds=5, equip=("Basic",)):
    incidents = [{"id": "I1", "severity": 3, "need": "Basic"}]
    ambs = [{"id": "A1", "equipment": list(equip)}]
    hosps = [{"name": "H1", "services": ["Basic"], "free": beds}]
    return build_world(incidents, ambs, hosps, {("A1", "I1"): response}, {("I1", "H1"): 4})


def test_hand_computed_utility():
    # Worst case is heavy traffic: response 15 -> 3 * (20 - 7.5) = 37.5
    result = minimax_decide(tiny_world(), 1)
    assert result["action"] == "I1" and abs(result["utility"] - 37.5) < 1e-9


def test_overload_penalty_and_unserved_penalty():
    # One bed: the hospital ends full (-5). Worst case is heavy traffic: 37.5 - 5 = 32.5
    assert abs(minimax_decide(tiny_world(beds=1), 1)["utility"] - 32.5) < 1e-9
    result = minimax_decide(tiny_world(equip=()), 1)             # no equipped ambulance
    assert abs(result["utility"] - (-3 * UNSERVED_PENALTY)) < 1e-9


def test_alphabeta_matches_minimax_on_default_scenario():
    for depth in (1, 2, 3, 4):
        r = run_workflow(default_scenario(), depth)
        assert r["minimax"]["action"] == r["alphabeta"]["action"]
        assert abs(r["minimax"]["utility"] - r["alphabeta"]["utility"]) < 1e-9
        assert r["alphabeta"]["nodes"] <= r["minimax"]["nodes"]


def test_alphabeta_prunes_at_depth_three():
    r = run_workflow(default_scenario(), 3)
    assert r["alphabeta"]["pruned"] > 0 and r["alphabeta"]["nodes"] < r["minimax"]["nodes"]


def test_agreement_on_random_scenarios():
    rng = random.Random(7)
    for _ in range(15):
        sc = default_scenario()
        for inc in sc["incidents"]:
            inc["severity"] = rng.randint(1, 5)
            inc["need"] = rng.choice(["Basic", "ICU", "Trauma"])
        for a in sc["ambulances"]:
            if rng.random() < 0.3:
                a["status"] = "Disabled"
        for h in sc["hospitals"]:
            h["total_beds"] = rng.randint(4, 9)
        sc["traffic"][edge_key("Central", "Market")] = rng.choice([1.0, 2.0, 4.0])
        r = run_workflow(sc, rng.randint(1, 3))
        assert r["minimax"]["action"] == r["alphabeta"]["action"]
        assert abs(r["minimax"]["utility"] - r["alphabeta"]["utility"]) < 1e-9


def test_edge_cases_no_incidents_or_ambulances():
    sc = default_scenario()
    for a in sc["ambulances"]:
        a["status"] = "Disabled"
    r = run_workflow(sc, 3)
    assert r["minimax"]["action"] is None and r["alphabeta"]["action"] is None
    assert r["minimax"]["utility"] == r["alphabeta"]["utility"] < 0
    sc = default_scenario()
    sc["incidents"] = []
    r = run_workflow(sc, 3)
    assert r["minimax"]["utility"] == 0 and r["alphabeta"]["utility"] == 0

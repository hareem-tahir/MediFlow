"""Tests for the CSP allocation."""
import copy
from mediflow.csp import solve, choose_variable
from mediflow.data import default_scenario
from mediflow.planner import plan


def test_default_scenario_all_assigned_and_valid():
    sc = default_scenario()
    prep, alloc = plan(sc)
    assert alloc["failed"] == [] and len(alloc["assignments"]) == 5
    ambs = [v[0] for v in alloc["assignments"].values()]
    assert len(ambs) == len(set(ambs))                       # each ambulance once
    equip = {a["id"]: a["equipment"] for a in sc["ambulances"]}
    services = {h["name"]: h["services"] for h in sc["hospitals"]}
    need = {i["id"]: i["need"] for i in sc["incidents"]}
    for inc, (amb, hosp, _, _) in alloc["assignments"].items():
        assert need[inc] in equip[amb] and need[inc] in services[hosp]
    for h in prep["hospitals"]:                              # capacity respected
        used = sum(1 for v in alloc["assignments"].values() if v[1] == h["name"])
        assert used <= h["free"]


def test_mrv_picks_smallest_domain_then_severity():
    domains = {"I1": [1, 2, 3], "I2": [1], "I3": [1]}
    assert choose_variable(domains, {"I1": 5, "I2": 2, "I3": 4}) == "I3"


def test_forward_checking_finds_solution_and_detects_dead_end():
    v = lambda amb, hosp: (amb, hosp, 10, 5)
    # Both incidents can use A1, but I1 only A1 -> I2 must take A2.
    result, _ = solve({"I1": [v("A1", "H1")], "I2": [v("A1", "H1"), v("A2", "H1")]},
                      {"I1": 3, "I2": 3}, {"H1": 2})
    assert result["I1"][0] == "A1" and result["I2"][0] == "A2"
    # Only one ambulance for two incidents -> impossible, forward checking prunes.
    result, stats = solve({"I1": [v("A1", "H1")], "I2": [v("A1", "H1")]}, {"I1": 3, "I2": 3}, {"H1": 2})
    assert result is None and stats["fc_prunes"] >= 1


def test_hospital_capacity_conflict():
    v = lambda amb, hosp: (amb, hosp, 10, 5)
    result, _ = solve({"I1": [v("A1", "H1")], "I2": [v("A2", "H1")]}, {"I1": 3, "I2": 3}, {"H1": 1})
    assert result is None


def test_too_few_ambulances_drops_lowest_severity_with_reason():
    sc = default_scenario()
    for a in sc["ambulances"]:
        if a["id"] in ("AMB-1", "AMB-5"):
            a["status"] = "Disabled"
    prep, alloc = plan(sc)
    assert len(alloc["assignments"]) == 3 and len(alloc["failed"]) == 2
    assert all(f["reason"] for f in alloc["failed"])
    assert "INC-4" in [f["incident"] for f in alloc["failed"]]    # lowest severity dropped first


def test_conflict_only_drops_the_incident_that_loses_the_conflict():
    sc = default_scenario()
    for a in sc["ambulances"]:
        if a["id"] in ("AMB-2", "AMB-4"):
            a["status"] = "Disabled"                 # only AMB-3 can take trauma cases
    _, alloc = plan(sc)
    failed = [f["incident"] for f in alloc["failed"]]
    assert sorted(failed) == ["INC-1", "INC-3"]
    assert "INC-5" in alloc["assignments"]           # higher severity trauma wins AMB-3
    assert len(alloc["assignments"]) == 3            # INC-2, INC-4, INC-5


def test_missing_equipment_is_explained():
    sc = default_scenario()
    for a in sc["ambulances"]:
        if "ICU" in a["equipment"]:
            a["status"] = "Disabled"
    _, alloc = plan(sc)
    failed = {f["incident"]: f["reason"] for f in alloc["failed"]}
    assert "ICU" in failed["INC-1"]


def test_full_hospitals_and_empty_input():
    sc = default_scenario()
    for h in sc["hospitals"]:
        h["total_beds"] = 0
    _, alloc = plan(sc)
    assert alloc["assignments"] == {} and len(alloc["failed"]) == 5
    sc["incidents"] = []
    _, alloc = plan(sc)
    assert alloc["assignments"] == {} and alloc["failed"] == []


def test_search_trace_is_recorded_and_readable():
    from mediflow.csp import trace_lines
    _, alloc = plan(default_scenario())
    assert len(alloc["rounds"]) == 5 and all(r["accepted"] for r in alloc["rounds"])
    last = alloc["rounds"][-1]
    kinds = [e["kind"] for e in last["trace"]]
    assert kinds[0] == "pick" and kinds[-1] == "solution" and "forward" in kinds
    assert last["trace"] and sum(k == "backtrack" for k in kinds) == last["stats"]["backtracks"]
    lines = trace_lines(last["trace"])
    assert any("MRV" in t for _, _, t in lines) and any("Forward checking" in t for _, _, t in lines)


def test_dropped_incident_round_shows_dead_end():
    from mediflow.csp import trace_lines
    sc = default_scenario()
    for a in sc["ambulances"]:
        if a["id"] in ("AMB-2", "AMB-4"):
            a["status"] = "Disabled"
    _, alloc = plan(sc)
    dropped = [r for r in alloc["rounds"] if not r["accepted"]]
    assert [r["incident"] for r in dropped] == ["INC-3"]
    assert any(i == "✖" for _, i, _ in trace_lines(dropped[0]["trace"]))


def test_trace_does_not_change_the_result():
    v = lambda amb, hosp: (amb, hosp, 10, 5)
    doms = {"I1": [v("A1", "H1")], "I2": [v("A1", "H1"), v("A2", "H1")]}
    plain, s1 = solve(doms, {"I1": 3, "I2": 3}, {"H1": 2})
    traced, s2 = solve(doms, {"I1": 3, "I2": 3}, {"H1": 2}, trace=[])
    assert plain == traced and s1 == s2


def test_plain_language_summary_covers_every_ambulance():
    from mediflow.csp import describe_plan
    sc = default_scenario()
    sc["ambulances"][4]["status"] = "Disabled"
    prep, alloc = plan(sc)
    sentences, rows = describe_plan(prep["incidents"], sc["ambulances"], alloc)
    assert len(sentences) == len(alloc["assignments"]) and len(rows) == 5
    assert "Out of service" in rows[4]["What it does"]
    assert all(r["What it does"] for r in rows)

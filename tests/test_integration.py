"""End-to-end tests: scenario -> routes -> CSP -> Minimax/Alpha-Beta -> app pages."""
import os
from streamlit.testing.v1 import AppTest
from mediflow.data import default_scenario, edge_key
from mediflow.planner import run_workflow
from mediflow.routing import astar, dijkstra

APP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")


def test_full_workflow_default():
    r = run_workflow(default_scenario(), 3)
    assert len(r["alloc"]["assignments"]) == 5
    assert r["minimax"]["action"] in r["world"]["incidents"]
    assert r["minimax"]["action"] == r["alphabeta"]["action"]


def test_road_closure_changes_allocation_times():
    base = run_workflow(default_scenario(), 2)["alloc"]["assignments"]
    sc = default_scenario()
    sc["blocked"] = [edge_key("Central", "Old Town"), edge_key("Old Town", "Riverside")]
    changed = run_workflow(sc, 2)["alloc"]["assignments"]
    assert sum(v[2] for v in changed.values()) != sum(v[2] for v in base.values())


def test_capacity_and_ambulance_shortage_flow_through():
    sc = default_scenario()
    for h in sc["hospitals"]:
        h["occupied"] = h["total_beds"] - 1          # one free bed each
    sc["incidents"].append({"id": "INC-9", "location": "Market", "severity": 1, "need": "Basic",
                            "status": "Open", "desc": "x", "amb": "", "hospital": ""})
    r = run_workflow(sc, 2)
    assert len(r["alloc"]["assignments"]) + len(r["alloc"]["failed"]) == 6
    assert len(r["alloc"]["assignments"]) <= 3        # only 3 beds exist


def test_workflow_routes_match_between_algorithms():
    r = run_workflow(default_scenario(), 1)
    adj = r["prep"]["adj"]
    for (amb_id, inc_id), cost in r["prep"]["amb_inc"].items():
        amb = next(a for a in r["prep"]["ambulances"] if a["id"] == amb_id)
        inc = next(i for i in r["prep"]["incidents"] if i["id"] == inc_id)
        assert abs(cost - dijkstra(adj, amb["base"], inc["location"])["cost"]) < 1e-9


def test_every_gui_page_loads_without_errors():
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception
    for page in at.sidebar.radio[0].options:
        at.sidebar.radio[0].set_value(page).run()
        assert not at.exception, f"{page} raised {at.exception}"
        assert "_page_error" not in at.session_state, at.session_state["_page_error"]   # friendly fallback never triggered
        assert not at.error, f"{page} shows a red error box"


def test_no_red_error_box_in_stressful_scenarios():
    """Closed roads, no ambulances, full hospitals: pages must explain, not show errors."""
    at = AppTest.from_file(APP, default_timeout=60).run()
    sc = at.session_state["scenario"]
    sc["blocked"] = [edge_key("Old Town", "Riverside"), edge_key("North Park", "Riverside"), edge_key("Riverside", "City General")]
    for a in sc["ambulances"]:
        a["status"] = "Disabled"
    for h in sc["hospitals"]:
        h["total_beds"] = 0
    for page in at.sidebar.radio[0].options:
        at.sidebar.radio[0].set_value(page).run()
        assert not at.exception and not at.error, page
        assert "_page_error" not in at.session_state, at.session_state["_page_error"]


def test_reset_button_restores_default():
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.session_state["scenario"]["blocked"] = [edge_key("Central", "Market")]
    at.sidebar.button[0].click().run()
    assert at.session_state["scenario"]["blocked"] == []

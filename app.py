"""MediFlow Control Center - Streamlit GUI for the emergency allocation simulator.
Run with:  streamlit run app.py
"""
import html
import os
import subprocess
import sys
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from mediflow.data import (NODES, ROADS, HOSPITAL_NODES, NEEDS, STATUSES,
                           edge_key, default_scenario, distance, base_cost)
from mediflow.routing import build_adjacency, compare, astar, dijkstra, unreachable_nodes
from mediflow.csp import trace_lines, describe_plan
from mediflow.planner import plan, make_world, free_beds, run_workflow
from mediflow.strategy import start_state, find_trip, minimax_decide, alphabeta_decide, decision_tree
from mediflow import cityview as cv
from mediflow.visuals import gantt_figure, sankey_figure

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGES = ["🏠 Overview Dashboard", "🚨 Emergency Management", "🗺️ Live Simulation Map", "🧭 Route Analysis",
         "🧩 Resource Allocation", "♟️ Strategic Planning", "🎛️ Scenario Controls", "📊 Evaluation and Reports"]
INCIDENT_ICON = {"Open": "🔴 Open", "Dispatched": "🟠 Dispatched", "Resolved": "🟢 Resolved"}
AMB_ICON = {"Available": "🟢 Available", "Busy": "🟠 Busy", "Disabled": "⚫ Disabled"}

st.set_page_config(page_title="MediFlow Control Center", page_icon="🚑", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1rem; max-width: 1500px;}
section[data-testid="stSidebar"] {background: #0a1226; border-right: 1px solid #1c2a47;}
section[data-testid="stSidebar"] .stRadio label {padding: 4px 2px;}
h2, h3, h4 {letter-spacing: .01em;}
.hdr {display: flex; align-items: center; gap: 18px; padding: 14px 22px; border-radius: 14px 14px 0 0;
      background: linear-gradient(100deg, #0f1b36 0%, #12254a 60%, #1a1630 100%); border: 1px solid #22304d; border-bottom: none;}
.hdr .logo {font-size: 2rem; filter: drop-shadow(0 0 8px rgba(239,68,68,.6));}
.hdr h1 {margin: 0; font-size: 1.55rem; color: #fff; letter-spacing: .04em; line-height: 1.1;}
.hdr p {margin: 0; color: #8aa0c0; font-size: .85rem;}
.hdr .pg {margin-left: auto; font-size: 1rem; color: #cbd5e1; font-weight: 600;}
.hdr .stat {font-size: .78rem; color: #86efac; letter-spacing: .08em; font-weight: 700; display: flex; align-items: center;}
.live {display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #22c55e; margin-right: 8px;
       animation: pulse 1.6s infinite;}
@keyframes pulse {0% {box-shadow: 0 0 0 0 rgba(34,197,94,.7);} 70% {box-shadow: 0 0 0 10px rgba(34,197,94,0);}
                  100% {box-shadow: 0 0 0 0 rgba(34,197,94,0);}}
.sirenbar {height: 4px; border-radius: 0 0 4px 4px; margin-bottom: 16px; background: #22304d;}
.sirenbar.on {background: linear-gradient(90deg, #ef4444 0 25%, #3b82f6 25% 50%, #ef4444 50% 75%, #3b82f6 75% 100%);
              background-size: 200% 100%; animation: sirenbar 1.2s linear infinite;}
@keyframes sirenbar {to {background-position: -200% 0;}}
.kpi {background: linear-gradient(180deg, #131c31, #0f1729); border: 1px solid #22304d; border-radius: 12px; padding: 12px 14px;
      border-top: 3px solid var(--k, #3b82f6);}
.kpi .l {font-size: .72rem; letter-spacing: .09em; text-transform: uppercase; color: #8aa0c0;}
.kpi .v {font-size: 1.85rem; font-weight: 700; color: #f8fafc; line-height: 1.15;}
.kpi .s {font-size: .78rem; color: #94a3b8;}
.kpi.red {--k: #ef4444;} .kpi.green {--k: #22c55e;} .kpi.amber {--k: #f59e0b;} .kpi.blue {--k: #3b82f6;}
.step {background: #131c31; border: 1px solid #243049; border-top: 4px solid #3b82f6; border-radius: 10px;
       padding: 10px 12px; min-height: 118px; font-size: .88rem;}
.step b {font-size: .95rem; color: #93c5fd;}
.step .big {font-size: 1.05rem; color: #f8fafc; display: block; margin-top: 6px;}
.alert {padding: 10px 16px; border-radius: 10px; margin-bottom: 12px; font-weight: 600;}
.alert.red {background: #450a0a; border: 1px solid #ef4444; color: #fecaca;}
.alert.green {background: #052e16; border: 1px solid #22c55e; color: #bbf7d0;}
.alert.amber {background: #451a03; border: 1px solid #f59e0b; color: #fde68a;}
.hrow {margin-bottom: 10px;} .hrow .t {display: flex; justify-content: space-between; font-size: .88rem; color: #dbe5f6;}
.hrow .bar {height: 9px; border-radius: 5px; background: #0a1020; border: 1px solid #22304d; overflow: hidden; margin-top: 4px;}
.hrow .bar i {display: block; height: 100%; border-radius: 5px;}
.sect {font-size: .75rem; letter-spacing: .1em; text-transform: uppercase; color: #8aa0c0; margin: 6px 0 6px; font-weight: 700;}
.cgrid {display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 12px;}
.cc {background: #101a30; border: 1px solid #22304d; border-radius: 12px; padding: 12px 14px; border-left: 5px solid #22c55e;}
.cc.bad {border-left-color: #ef4444; background: #1a1220;}
.cc .ch {display: flex; align-items: center; gap: 8px; margin-bottom: 8px; flex-wrap: wrap;}
.cc .sv {width: 24px; height: 24px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center;
         font-weight: 800; color: #fff; font-size: .8rem;}
.cc .mu {color: #8aa0c0; font-size: .82rem; flex: 1;} .cc .need {font-size: .72rem; padding: 2px 8px; border-radius: 10px; background: #1d2b4a; color: #a9bde0;}
.cc .flow {display: flex; align-items: center; gap: 8px; margin: 4px 0 8px; flex-wrap: wrap;}
.cc .pill {padding: 4px 10px; border-radius: 8px; font-weight: 700; font-size: .85rem;}
.cc .pill.a {background: #1e3a8a; color: #dbeafe;} .cc .pill.i {background: #7f1d1d; color: #fee2e2;}
.cc .pill.h {background: #0f766e; color: #ccfbf1;} .cc .pill.x {background: #7f1d1d; color: #fecaca;}
.cc .ar {color: #64748b;}
.cc .ck {font-size: .82rem; padding: 2px 0; color: #cbd5e1;} .cc .ck b {display: inline-block; width: 20px;}
.cc .ck.y b {color: #4ade80;} .cc .ck.n b {color: #f87171;}
.cc .why {font-size: .8rem; margin-top: 6px; padding: 6px 8px; border-radius: 8px; background: #0b1426; color: #9fb3d6;}
.cc .why.bad {background: #2a0f16; color: #fecaca;}
.cc .why b {display: block; margin-bottom: 3px; color: #cbd5e1;}
.cc .op {padding: 1px 0; font-size: .8rem; color: #9fb3d6;} .cc .op.on {color: #86efac; font-weight: 600;}
.cc .op b {display: inline-block; width: 18px;}
.trace {background: #0b1426; border: 1px solid #22304d; border-radius: 10px; padding: 10px 12px; max-height: 520px; overflow-y: auto;
        font-size: .84rem; color: #cbd5e1; line-height: 1.5;}
.trace div {padding: 2px 0; border-left: 2px solid #22304d; padding-left: 8px;}
.trace .t-pick {color: #93c5fd;} .trace .t-bad {color: #fca5a5;} .trace .t-ok {color: #86efac; font-weight: 600;} .trace .t-undo {color: #fcd34d;}
.how {background: #101a30; border: 1px solid #22304d; border-radius: 10px; padding: 10px 14px; font-size: .88rem; color: #cbd5e1;}
iframe {border-radius: 14px;}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------ scenario state
if "scenario" not in st.session_state:
    st.session_state.scenario = default_scenario()
sc = st.session_state.scenario


def log(message):
    sc["log"].insert(0, f"{datetime.now().strftime('%H:%M:%S')}  {message}")


def notify(kind, message):
    """Show a message after the page reloads (kind = success / warning / error)."""
    st.session_state.flash = (kind, message)
    st.rerun()


def road_label(key):
    return f"{key[0]} ↔ {key[1]}"


def scenario_signature():
    return str((sc["traffic"], sc["blocked"], sc["incidents"], sc["ambulances"], sc["hospitals"]))


def release_ambulance(inc):
    for a in sc["ambulances"]:
        if a["id"] == inc["amb"] and a["status"] == "Busy":
            a["status"] = "Available"


def reopen(inc):
    """Undo a dispatch: free the ambulance and the hospital bed."""
    release_ambulance(inc)
    if inc["status"] == "Dispatched":
        for h in sc["hospitals"]:
            if h["name"] == inc["hospital"]:
                h["occupied"] = max(0, h["occupied"] - 1)
    inc["amb"], inc["hospital"] = "", ""


def commit_dispatch(inc_id, amb_id, hospital):
    """Make one dispatch real: the ambulance becomes busy and the hospital uses a bed."""
    inc = next(i for i in sc["incidents"] if i["id"] == inc_id)
    inc.update(status="Dispatched", amb=amb_id, hospital=hospital)
    next(a for a in sc["ambulances"] if a["id"] == amb_id)["status"] = "Busy"
    next(h for h in sc["hospitals"] if h["name"] == hospital)["occupied"] += 1


def apply_allocation(alloc):
    """Dispatch every CSP assignment: ambulances become busy, beds get used."""
    for inc_id, (amb, hosp, _, _) in alloc["assignments"].items():
        commit_dispatch(inc_id, amb, hosp)
    log(f"Dispatched {len(alloc['assignments'])} assignment(s)")
    notify("success", "Plan dispatched: ambulances are busy and hospital beds are used.")


def add_incident(loc, need, sev, desc):
    number = max([int(i["id"].split("-")[1]) for i in sc["incidents"]] + [0]) + 1
    new_id = f"INC-{number}"
    sc["incidents"].append({"id": new_id, "location": loc, "severity": sev, "need": need,
                            "status": "Open", "desc": desc, "amb": "", "hospital": ""})
    log(f"Registered {new_id} at {loc} (severity {sev}, needs {need})")
    return new_id


def city_missions(prep, alloc, manual=None):
    """Missions drawn on the map: dispatches already committed + the planned ones
    (the CSP plan, or a single manual dispatch)."""
    done = cv.build_missions(prep["adj"], sc, cv.committed_triples(sc), "committed")
    triples = manual if manual is not None else [(i, v[0], v[1]) for i, v in alloc["assignments"].items()]
    return done + cv.build_missions(prep["adj"], sc, triples, "planned", color_offset=len(done))


def show_html(html, height):
    """Embed one of the HTML/SVG views. Falls back to st.iframe on Streamlit versions without components.html."""
    try:
        components.html(html, height=height, scrolling=False)
    except Exception:
        try:
            st.iframe(html, height=height)
        except Exception:
            st.info("This interactive view could not be shown in the current browser session.")


def kpi(label, value, sub="", tone="blue"):
    return f'<div class="kpi {tone}"><div class="l">{label}</div><div class="v">{value}</div><div class="s">{sub}</div></div>'



def dark(fig, height=300):
    """Common look for ordinary charts."""
    fig.update_layout(height=height, margin=dict(l=5, r=5, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#cbd5e1"))
    return fig


# ------------------------------------------------------------------ pages
def page_overview():
    prep, alloc = plan(sc)
    flow = run_workflow(sc, 3)
    incidents = sc["incidents"]
    open_inc = [i for i in incidents if i["status"] == "Open"]
    critical = [i for i in open_inc if i["severity"] >= 4]
    total_beds = sum(h["total_beds"] for h in sc["hospitals"])
    used = sum(min(h["occupied"], h["total_beds"]) for h in sc["hospitals"])
    free = sum(free_beds(h) for h in sc["hospitals"])
    etas = [v[3] for v in alloc["assignments"].values()]
    n_amb = len(sc["ambulances"])

    if critical:
        st.markdown(f'<div class="alert red">🔴 {len(critical)} critical emergency(ies) waiting: '
                    f'{", ".join(i["id"] for i in critical)}</div>', unsafe_allow_html=True)
    elif open_inc:
        st.markdown('<div class="alert amber">🟠 Open emergencies, none critical.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert green">🟢 All clear - no open emergencies.</div>', unsafe_allow_html=True)

    k = st.columns(6)
    k[0].markdown(kpi("Open emergencies", len(open_inc), f"{len(critical)} critical (sev 4-5)", "red"), unsafe_allow_html=True)
    k[1].markdown(kpi("Active dispatches", sum(i["status"] == "Dispatched" for i in incidents), "ambulances on mission", "amber"), unsafe_allow_html=True)
    k[2].markdown(kpi("Ambulances ready", f"{sum(a['status'] == 'Available' for a in sc['ambulances'])}/{n_amb}",
                      f"{sum(a['status'] == 'Disabled' for a in sc['ambulances'])} out of service", "green"), unsafe_allow_html=True)
    k[3].markdown(kpi("Hospital beds free", free, f"{used}/{total_beds} occupied", "blue"), unsafe_allow_html=True)
    k[4].markdown(kpi("Avg response", f"{sum(etas) / len(etas):.1f} min" if etas else "n/a", "CSP plan, A* routes", "blue"), unsafe_allow_html=True)
    k[5].markdown(kpi("Road alerts", len(sc["blocked"]) + len(sc["traffic"]), f"{len(sc['blocked'])} closed · {len(sc['traffic'])} congested",
                      "amber" if sc["blocked"] or sc["traffic"] else "green"), unsafe_allow_html=True)
    st.write("")

    left, right = st.columns([5, 2])
    with left:
        st.markdown('<div class="sect">City operations map · press “Run dispatch” to watch the plan play out</div>', unsafe_allow_html=True)
        show_html(cv.dispatch_map_html(sc, prep["adj"], city_missions(prep, alloc), panel=False, height=620), 625)
    with right:
        st.markdown('<div class="sect">Hospital capacity</div>', unsafe_allow_html=True)
        for h in sc["hospitals"]:
            occ = min(h["occupied"], h["total_beds"])
            ratio = occ / h["total_beds"] if h["total_beds"] else 1.0
            col = "#22c55e" if ratio < .6 else "#f59e0b" if ratio < .85 else "#ef4444"
            tag = " · <b style='color:#f87171'>FULL</b>" if free_beds(h) == 0 else ""
            st.markdown(f'<div class="hrow"><div class="t"><span>🏥 <b>{h["name"]}</b>{tag}</span><span>{occ}/{h["total_beds"]}</span></div>'
                        f'<div class="bar"><i style="width:{ratio * 100:.0f}%;background:{col}"></i></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="sect">Ambulance fleet</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame([{"Unit": a["id"], "Base": a["base"], "Equipment": ", ".join(a["equipment"]),
                                    "Status": AMB_ICON[a["status"]]} for a in sc["ambulances"]]), hide_index=True)
        st.markdown('<div class="sect">Recent activity</div>', unsafe_allow_html=True)
        for line in sc["log"][:5]:
            st.caption("• " + line)

    st.markdown("#### Decision pipeline (live results for the current scenario)")
    mm, ab = flow["minimax"], flow["alphabeta"]
    steps = [
        ("1 · Incident registration", f"{len(open_inc)} open", f"{len(incidents)} emergencies on record"),
        ("2 · Route planning (A*)", f"{len(prep['amb_inc']) + len(prep['inc_hosp'])} trips routed",
         f"blocked roads: {len(sc['blocked'])}, traffic roads: {len(sc['traffic'])}"),
        ("3 · CSP allocation", f"{len(alloc['assignments'])} / {len(prep['incidents'])} assigned",
         f"{len(alloc['failed'])} failed, {alloc['stats']['backtracks']} backtracks"),
        ("4 · Minimax / Alpha-Beta", f"dispatch {mm['action']} first" if mm["action"] else "nothing to plan",
         f"{ab['nodes']} of {mm['nodes']} nodes, same decision: {mm['action'] == ab['action']}"),
        ("5 · Dashboard", "plan ready" if alloc["assignments"] else "no plan", "open the Live Simulation Map"),
    ]
    for col, (title, big, small) in zip(st.columns(5), steps):
        col.markdown(f'<div class="step"><b>{title}</b><span class="big">{big}</span>{small}</div>', unsafe_allow_html=True)

def page_incidents():
    st.subheader("Emergencies")
    shown = st.multiselect("Filter by status", STATUSES, default=STATUSES)
    rows = [{"ID": i["id"], "Status": INCIDENT_ICON[i["status"]], "Severity": i["severity"], "Location": i["location"],
             "Need": i["need"], "Ambulance": i["amb"], "Hospital": i["hospital"], "Description": i["desc"]}
            for i in sorted(sc["incidents"], key=lambda i: -i["severity"]) if i["status"] in shown]
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True, column_config={
            "Severity": st.column_config.ProgressColumn("Severity", min_value=0, max_value=5, format="%d")})
    else:
        st.info("No emergencies match this filter.")

    tab_new, tab_edit = st.tabs(["➕ Register emergency", "✏️ Edit / manage"])
    places = [n for n in NODES if n not in HOSPITAL_NODES]
    with tab_new:
        with st.form("register"):
            c1, c2 = st.columns(2)
            loc = c1.selectbox("Location", places)
            need = c2.selectbox("Patient requirement", NEEDS)
            sev = st.slider("Severity (1 = minor, 5 = critical)", 1, 5, 3)
            desc = st.text_input("Description", "New emergency")
            if st.form_submit_button("🚨 Register emergency"):
                new_id = add_incident(loc, need, sev, desc)
                notify("success", f"{new_id} registered.")
    with tab_edit:
        if not sc["incidents"]:
            st.info("No emergencies to edit.")
            return
        inc = next(i for i in sc["incidents"] if i["id"] == st.selectbox("Select emergency", [i["id"] for i in sc["incidents"]]))
        allowed = STATUSES if inc["status"] == "Dispatched" else ["Open", "Resolved"]
        with st.form("edit"):
            c1, c2 = st.columns(2)
            loc = c1.selectbox("Location", places, index=places.index(inc["location"]))
            need = c2.selectbox("Patient requirement", NEEDS, index=NEEDS.index(inc["need"]))
            sev = st.slider("Severity", 1, 5, inc["severity"])
            status = st.selectbox("Status", allowed, index=allowed.index(inc["status"]))
            desc = st.text_input("Description", inc["desc"])
            save = st.form_submit_button("Save changes")
            delete = st.form_submit_button("Delete emergency")
        if save:
            if status != inc["status"]:
                if status == "Open":
                    reopen(inc)
                elif status == "Resolved":
                    release_ambulance(inc)
            inc.update(location=loc, severity=sev, need=need, status=status, desc=desc)
            log(f"Updated {inc['id']} (status {status})")
            notify("success", f"{inc['id']} updated.")
        if delete:
            reopen(inc)
            sc["incidents"].remove(inc)
            log(f"Deleted {inc['id']}")
            notify("warning", f"{inc['id']} deleted.")


def quick_controls():
    """Compact controls that change the scenario; the map above updates on the next run."""
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="sect">🚨 Add incident</div>', unsafe_allow_html=True)
        places = [n for n in NODES if n not in HOSPITAL_NODES]
        loc = st.selectbox("Location", places, key="qc_loc")
        need = st.selectbox("Needs", NEEDS, key="qc_need")
        sev = st.slider("Severity", 1, 5, 4, key="qc_sev")
        if st.button("Add incident", key="qc_add"):
            new_id = add_incident(loc, need, sev, "Reported from control room")
            notify("success", f"{new_id} added at {loc}.")
    with c2:
        st.markdown('<div class="sect">🚧 Roads</div>', unsafe_allow_html=True)
        roads = [edge_key(a, b) for a, b in ROADS]
        road = st.selectbox("Road", roads, format_func=road_label, key="qc_road")
        act = st.radio("Action", ["Block", "Reopen", "Traffic"], horizontal=True, key="qc_act")
        mult = st.slider("Traffic multiplier", 1.0, 5.0, 3.0, 0.5, key="qc_mult", disabled=act != "Traffic")
        if st.button("Apply to road", key="qc_road_go"):
            if act == "Block" and road not in sc["blocked"]:
                sc["blocked"].append(road)
            elif act == "Reopen" and road in sc["blocked"]:
                sc["blocked"].remove(road)
            elif act == "Traffic":
                if mult == 1.0:
                    sc["traffic"].pop(road, None)
                else:
                    sc["traffic"][road] = mult
            log(f"{act} {road_label(road)}" + (f" x{mult:.1f}" if act == "Traffic" else ""))
            notify("success", f"{act}: {road_label(road)}")
    with c3:
        st.markdown('<div class="sect">🚑 Ambulance availability</div>', unsafe_allow_html=True)
        amb = next(a for a in sc["ambulances"] if a["id"] == st.selectbox(
            "Ambulance", [a["id"] for a in sc["ambulances"]], format_func=lambda i: f"{i} ({next(a['status'] for a in sc['ambulances'] if a['id'] == i)})",
            key="qc_amb"))
        if amb["status"] == "Busy":
            st.caption("This unit is on a mission; resolve the emergency to free it.")
        elif st.button("Return to service" if amb["status"] == "Disabled" else "Make unavailable", key="qc_amb_go"):
            amb["status"] = "Available" if amb["status"] == "Disabled" else "Disabled"
            log(f"{amb['id']} is now {amb['status']}")
            notify("success", f"{amb['id']} is now {amb['status'].lower()}.")
    with c4:
        st.markdown('<div class="sect">🏥 Hospital capacity</div>', unsafe_allow_html=True)
        hname = st.selectbox("Hospital", [h["name"] for h in sc["hospitals"]], key="qc_hosp")
        hosp = next(h for h in sc["hospitals"] if h["name"] == hname)
        st.caption(f"{free_beds(hosp)} free of {hosp['total_beds']} beds ({hosp['occupied']} occupied)")
        b1, b2 = st.columns(2)
        if b1.button("− 1 bed", key="qc_bed_dn"):
            hosp["total_beds"] = max(0, hosp["total_beds"] - 1)
            log(f"{hname} capacity reduced to {hosp['total_beds']}")
            notify("warning", f"{hname} now has {free_beds(hosp)} free bed(s).")
        if b2.button("+ 1 bed", key="qc_bed_up"):
            hosp["total_beds"] = min(30, hosp["total_beds"] + 1)
            log(f"{hname} capacity raised to {hosp['total_beds']}")
            notify("success", f"{hname} now has {free_beds(hosp)} free bed(s).")


def manual_dispatch_ui(prep):
    """Pick any ambulance, emergency and hospital; constraints are checked live. Returns the planned triple list."""
    avail = [a for a in sc["ambulances"] if a["status"] == "Available"]
    open_inc = [i for i in sc["incidents"] if i["status"] == "Open"]
    if not avail or not open_inc:
        st.info("Manual dispatch needs an available ambulance and an open emergency.")
        return []
    c1, c2, c3 = st.columns(3)
    amb = next(a for a in avail if a["id"] == c1.selectbox("Ambulance", [a["id"] for a in avail], key="md_amb"))
    inc = next(i for i in open_inc if i["id"] == c2.selectbox("Emergency", [i["id"] for i in open_inc], key="md_inc"))
    hosp = next(h for h in sc["hospitals"] if h["name"] == c3.selectbox("Destination hospital", [h["name"] for h in sc["hospitals"]], key="md_hosp"))
    r1 = astar(prep["adj"], amb["base"], inc["location"])
    r2 = astar(prep["adj"], inc["location"], hosp["name"])
    checks = [(inc["need"] in amb["equipment"], f"Equipment: {amb['id']} carries {', '.join(amb['equipment'])}; patient needs {inc['need']}"),
              (inc["need"] in hosp["services"], f"Service: {hosp['name']} offers {', '.join(hosp['services'])}"),
              (free_beds(hosp) > 0, f"Capacity: {hosp['name']} has {free_beds(hosp)} free bed(s)"),
              (bool(r1["route"] and r2["route"]), "Route: " + (f"{r1['cost']:.1f} min to scene + {r2['cost']:.1f} min to hospital"
                                                             if r1["route"] and r2["route"] else "no open road connects these places"))]
    st.markdown("".join(f'<div class="cc" style="border:none;padding:1px 0;background:none"><div class="ck {"y" if ok else "n"}"><b>{"✔" if ok else "✖"}</b>{t}</div></div>'
                        for ok, t in checks), unsafe_allow_html=True)
    legal = all(ok for ok, _ in checks)
    if legal and st.button("🚑 Commit this dispatch", key="md_go"):
        commit_dispatch(inc["id"], amb["id"], hosp["name"])
        log(f"Manual dispatch: {amb['id']} → {inc['id']} → {hosp['name']}")
        notify("success", f"{amb['id']} dispatched to {inc['id']}.")
    elif not legal:
        st.caption("The CSP constraints are not all satisfied, so this dispatch is disabled.")
    return [(inc["id"], amb["id"], hosp["name"])] if r1["route"] and r2["route"] else []


def page_map():
    prep, alloc = plan(sc)
    mode = st.radio("Dispatch plan", ["🧠 AI plan (CSP allocation)", "🕹️ Manual dispatch"], horizontal=True, label_visibility="collapsed")
    manual = None
    if mode.startswith("🕹️"):
        manual = manual_dispatch_ui(prep)
    missions = city_missions(prep, alloc, manual)
    if not prep["incidents"] and not missions:
        st.info("No open emergencies. Add one with the quick controls below.")
    elif not [m for m in missions if m["status"] == "planned"] and not [m for m in missions if m["status"] == "committed"]:
        st.info("No ambulance could be matched to an open emergency yet, so nothing is driving. Resource Allocation explains why.")
    show_html(cv.dispatch_map_html(sc, prep["adj"], missions, panel=True, height=760), 765)
    planned = [m for m in missions if m["status"] == "planned"]
    if alloc["failed"] and manual is None:
        st.warning("Not served: " + ", ".join(f"{f['incident']} ({f['reason']})" for f in alloc["failed"]))
    if manual is None and alloc["assignments"]:
        if st.button("🚑 Commit this plan (ambulances become busy, beds are used)"):
            apply_allocation(alloc)
    elif manual is None:
        st.caption("Nothing to commit right now.")

    tab_ctl, tab_time = st.tabs(["⚙️ Scenario controls", "🗓️ Mission timeline"])
    with tab_ctl:
        quick_controls()
    with tab_time:
        if missions:
            st.plotly_chart(dark(gantt_figure(missions), 60 + 42 * len(missions)))
            st.caption("Blue = driving to the scene, amber = patient transport (minutes from dispatch, from the real A* travel times).")
        else:
            st.info("No missions to show.")

def page_routes():
    st.subheader("A* vs Dijkstra on the same trip")
    adj = build_adjacency(sc["traffic"], sc["blocked"])
    c1, c2 = st.columns(2)
    start = c1.selectbox("From", list(NODES), index=list(NODES).index("Harbor"))
    goal = c2.selectbox("To", list(NODES), index=list(NODES).index("North Med"))
    a, d = compare(adj, start, goal)
    ta, td = astar(adj, start, goal, trace=True), dijkstra(adj, start, goal, trace=True)   # step-by-step traces
    if not a["route"]:
        st.info(f"There is currently no open road connecting {start} and {goal}, so there is no route to compare.")

    m = st.columns(4)
    m[0].metric("A* explored", a["explored"])
    m[1].metric("Dijkstra explored", d["explored"], f"{a['explored'] - d['explored']:+d} for A*", delta_color="off")
    m[2].metric("Route cost", f"{a['cost']:.2f} min" if a["route"] else "no route")
    m[3].metric("Same cost?", "✅ yes" if abs(a["cost"] - d["cost"]) < 1e-9 else "❌ no")

    st.markdown('<div class="sect">Step-through search · same graph, same trip · press “Play search”</div>', unsafe_allow_html=True)
    show_html(cv.search_html(sc, start, goal, ta, td, a_stats=a, d_stats=d), 860)

    st.dataframe(pd.DataFrame([
        {"Algorithm": "A*", "Route": " → ".join(a["route"]), "Cost (min)": round(a["cost"], 2),
         "Avg time (ms)": round(a["time_ms"], 4), "Explored nodes": a["explored"]},
        {"Algorithm": "Dijkstra", "Route": " → ".join(d["route"]), "Cost (min)": round(d["cost"], 2),
         "Avg time (ms)": round(d["time_ms"], 4), "Explored nodes": d["explored"]}]), hide_index=True)

    if a["route"] and len(a["route"]) > 1:
        st.markdown("**Cost of every road on the chosen route** (this is the weight the algorithms add up)")
        legs, total = [], 0.0
        for p, q in zip(a["route"], a["route"][1:]):
            w = dict(adj[p])[q]
            total += w
            mult = sc["traffic"].get(edge_key(p, q), 1.0)
            legs.append({"Road": f"{p} → {q}", "Distance": round(distance(p, q), 2), "Clear-road time (min)": round(base_cost(p, q), 2),
                         "Traffic": f"x{mult:.1f}" if mult > 1 else "clear", "Time used (min)": round(w, 2), "Running total (min)": round(total, 2)})
        st.dataframe(pd.DataFrame(legs), hide_index=True)

    # Plain-language explanation built from the real numbers.
    if a["explored"] < d["explored"]:
        st.write(f"A* expanded {d['explored'] - a['explored']} fewer nodes because the straight-line heuristic pulls "
                 "the search toward the goal. Dijkstra spreads out in every direction by cost alone.")
    elif a["explored"] == d["explored"]:
        st.write("Both expanded the same number of nodes here: the heuristic had nothing to save on this trip.")
    else:
        st.write("A* expanded more nodes here: a detour made the heuristic misleading, but the answer is still optimal.")
    faster = "A*" if a["time_ms"] < d["time_ms"] else "Dijkstra"
    st.caption(f"{faster} was faster on average over 100 runs. On a graph this small, Python overhead matters "
               "more than the nodes saved.")

def csp_walkthrough(prep, alloc):
    """Show how the CSP actually ran: the problem, each round, and the recorded search steps."""
    st.markdown("#### How the CSP found this plan")
    n_inc = len(prep["incidents"])
    sizes = ", ".join(f"{k}: {len(v)}" for k, v in alloc["domains"].items())
    st.markdown(
        f'<div class="how"><b>The puzzle.</b> {n_inc} emergencies each need one value = (ambulance, hospital). '
        f'Legal values per emergency (the "domain"): {sizes}.<br>'
        '<b>Rules (constraints).</b> The ambulance carries the needed equipment · the hospital offers the needed care and has a free bed · '
        'one ambulance serves one emergency · a hospital cannot take more patients than its free beds.<br>'
        '<b>Search.</b> Backtracking with <b>MRV</b> (always handle the emergency with the fewest legal options first) and '
        '<b>forward checking</b> (after every choice, remove the options it breaks from the other emergencies; if one runs out of options, undo the choice at once).<br>'
        '<b>Priority.</b> Emergencies are added one round at a time, most severe first. A round keeps an emergency only if a full valid plan still exists with it.</div>',
        unsafe_allow_html=True)
    rounds = alloc.get("rounds", [])
    if not rounds:
        st.caption("No search was needed for this scenario.")
        return
    st.dataframe(pd.DataFrame([{
        "Round": n, "Emergency added": r["incident"], "Severity": r["severity"], "Already accepted": ", ".join(r["with"]) or "none",
        "Result": "kept in the plan" if r["accepted"] else "dropped (no valid plan with it)",
        "Search calls": r["stats"]["calls"], "Undone choices": r["stats"]["backtracks"], "Dead ends found by forward checking": r["stats"]["fc_prunes"]}
        for n, r in enumerate(rounds, 1)]), hide_index=True)
    labels = [f"Round {n}: add {r['incident']} - {'kept' if r['accepted'] else 'dropped'}" for n, r in enumerate(rounds, 1)]
    pick = st.selectbox("Show the search steps of", labels, index=len(labels) - 1)
    r = rounds[labels.index(pick)]
    rows = []
    for depth, icon, text in trace_lines(r["trace"]):
        cls = "t-pick" if icon == "🎯" else "t-bad" if icon == "✖" else "t-undo" if icon == "↩" else "t-ok" if icon == "✔" else ""
        rows.append(f'<div class="{cls}" style="margin-left:{depth * 18}px">{icon} {html.escape(text)}</div>')
    if not r["accepted"]:
        rows.append('<div class="t-bad">✖ Every option for the emergency just added led to a dead end, so it is dropped and the earlier plan stays.</div>')
    st.markdown(f'<div class="trace">{"".join(rows)}</div>', unsafe_allow_html=True)
    st.caption("These are the real steps recorded while the solver ran. Indentation = how many emergencies are already fixed.")


def page_allocation():
    prep, alloc = plan(sc)
    st.subheader("CSP allocation (backtracking + MRV + forward checking)")
    if not prep["incidents"]:
        st.info("There are no open emergencies to allocate.")
        return
    if not prep["ambulances"]:
        st.warning("No ambulance is available - every emergency will fail.")
    stats = alloc["stats"]
    c = st.columns(4)
    c[0].metric("Assigned", f"{len(alloc['assignments'])} / {len(prep['incidents'])}")
    c[1].metric("Search calls", stats["calls"])
    c[2].metric("Backtracks", stats["backtracks"])
    c[3].metric("Forward-check prunes", stats["fc_prunes"])

    sev = {i["id"]: i for i in prep["incidents"]}
    if alloc["assignments"]:
        st.success(f"{len(alloc['assignments'])} emergency(ies) successfully allocated.")
    if alloc["failed"]:
        st.warning(f"{len(alloc['failed'])} emergency(ies) are not served in this plan. The cards below say why.")
    sentences, amb_rows = describe_plan(prep["incidents"], sc["ambulances"], alloc)
    if sentences:
        st.markdown('<div class="sect">Who goes where (plain language)</div>', unsafe_allow_html=True)
        st.markdown("\n".join(f"- {t}" for t in sentences))
    st.markdown('<div class="sect">What every ambulance is doing</div>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(amb_rows), hide_index=True)
    st.caption("An ambulance serves one emergency and then carries that patient to a hospital. "
               "Each emergency is matched with exactly one ambulance and one hospital.")
    st.markdown('<div class="sect">Assignments and the constraints checked for each emergency</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="cgrid">{cv.csp_cards_html(prep, alloc)}</div>', unsafe_allow_html=True)
    st.write("")
    if alloc["assignments"]:
        st.markdown("**Allocation flow: emergency → ambulance → hospital** (red = severity 4-5)")
        st.plotly_chart(sankey_figure(alloc, prep["incidents"]))
        st.dataframe(pd.DataFrame([
            {"Incident": k, "Severity": sev[k]["severity"], "Need": sev[k]["need"], "Ambulance": v[0],
             "Hospital": v[1], "Response (min)": v[3], "Total trip (min)": v[2]}
            for k, v in sorted(alloc["assignments"].items(), key=lambda kv: -sev[kv[0]]["severity"])]), hide_index=True)
        if st.button("🚑 Dispatch these assignments"):
            apply_allocation(alloc)

    csp_walkthrough(prep, alloc)

    left, right = st.columns(2)
    with left:
        st.markdown("**Compatible options per emergency**")
        st.dataframe(pd.DataFrame([{"Incident": k, "Need": sev[k]["need"],
                                    "Ambulances": ", ".join(sorted({v[0] for v in vals})) or "none",
                                    "Hospitals": ", ".join(sorted({v[1] for v in vals})) or "none",
                                    "Legal pairs": len(vals)} for k, vals in alloc["domains"].items()]), hide_index=True)
    with right:
        st.markdown("**Hospital capacity vs planned use**")
        used = {h["name"]: 0 for h in prep["hospitals"]}
        for v in alloc["assignments"].values():
            used[v[1]] += 1
        st.dataframe(pd.DataFrame([{"Hospital": h["name"], "Services": ", ".join(h["services"]), "Free beds": h["free"],
                                    "Planned": used[h["name"]], "Left": h["free"] - used[h["name"]]}
                                   for h in prep["hospitals"]]), hide_index=True)


def page_strategy():
    st.subheader("Minimax vs Alpha-Beta")
    prep, _ = plan(sc)
    world = make_world(prep)
    if not world["incidents"]:
        st.info("There are no open emergencies to plan for.")
        return
    if not world["ambs"]:
        st.warning("No ambulance is available, so every patient would be unserved.")
    with st.expander("How the game is defined"):
        st.markdown("""
* **MAX (dispatcher)** chooses which open emergency to dispatch next (nearest compatible ambulance and hospital are used).
* **MIN (adversary)** answers with the worst event: *heavy traffic* (response x1.5), *hospital overload* (one extra bed lost), or *ambulance out of service* (most capable free ambulance lost).
* **Terminal:** depth limit reached, no emergencies left, or no ambulance left.
* **Utility:** `+ severity x (20 - 0.5 x response minutes)` per served patient, `- severity x 15` per unserved patient, `- 5` when a hospital ends with no free beds.
""")
    depth = st.slider("Search depth (dispatches to look ahead)", 1, 4, min(3, len(world["incidents"])))
    if st.button("▶ Run Minimax and Alpha-Beta"):
        st.session_state.strategy = {"mm": minimax_decide(world, depth), "ab": alphabeta_decide(world, depth),
                                     "tree_mm": decision_tree(world, depth, False), "tree_ab": decision_tree(world, depth, True),
                                     "depth": depth, "sig": scenario_signature()}
    res = st.session_state.get("strategy")
    if not res:
        st.info("Press the button to run both algorithms on the current scenario.")
        return
    if res["sig"] != scenario_signature():
        st.warning("The scenario changed after this run. Press the button again for fresh results.")
    mm, ab, depth = res["mm"], res["ab"], res["depth"]
    if mm["action"] is None:
        st.info("Nothing to decide at this depth.")
        return
    if mm["action"] == ab["action"] and abs(mm["utility"] - ab["utility"]) < 1e-9:
        st.success(f"Both algorithms agree: dispatch **{mm['action']}** first (worst-case utility {mm['utility']:.2f}).")
    else:
        st.info(f"Minimax prefers {mm['action']} and Alpha-Beta prefers {ab['action']} at this depth; compare their utilities below.")
    saved = 1 - ab["nodes"] / mm["nodes"] if mm["nodes"] else 0
    c = st.columns(4)
    c[0].metric("Minimax nodes", mm["nodes"])
    c[1].metric("Alpha-Beta nodes", ab["nodes"], f"-{saved:.0%}", delta_color="off")
    c[2].metric("Pruning cutoffs", ab["pruned"])
    c[3].metric("Utility (both)", f"{mm['utility']:.2f}")
    st.caption(f"Time (single run, depth {depth}): Minimax {mm['time_ms']:.1f} ms, Alpha-Beta {ab['time_ms']:.1f} ms.")

    st.markdown('<div class="sect">Decision trees from the real searches · press “Replay” to watch the evaluation order</div>', unsafe_allow_html=True)
    show_html(cv.tree_html(res["tree_mm"], res["tree_ab"]), min(cv.tree_height(res["tree_mm"]), 1500))

    left, right = st.columns(2)
    with left:
        st.markdown("**Alternative plans (Minimax worst-case utility)**")
        rows = []
        for inc_id, value in sorted(mm["values"].items(), key=lambda kv: -kv[1]):
            trip = find_trip(world, start_state(world), inc_id)
            rows.append({"Dispatch first": inc_id, "Severity": world["severity"][inc_id],
                         "Ambulance": trip["amb"] if trip else "none", "Hospital": trip["hospital"] if trip else "none",
                         "Utility": round(value, 2), "Chosen": "✅" if inc_id == mm["action"] else ""})
        st.dataframe(pd.DataFrame(rows), hide_index=True)
    with right:
        st.markdown("**Nodes evaluated per first plan** - the gap is the pruning")
        fig = go.Figure()
        fig.add_bar(name="Minimax", x=list(mm["per_plan"]), y=list(mm["per_plan"].values()), marker_color="#3b82f6")
        fig.add_bar(name="Alpha-Beta", x=list(ab["per_plan"]), y=list(ab["per_plan"].values()), marker_color="#ef4444")
        fig.update_layout(barmode="group", legend=dict(orientation="h", y=1.15))
        st.plotly_chart(dark(fig, 300))


PRESETS = {
    "🚦 Rush hour": "Heavy traffic on every road touching Central",
    "🌊 Flooded district": "Three roads closed around Riverside and Harbor",
    "🏥 Hospital surge": "Every hospital has only one free bed",
    "🚑 Ambulance shortage": "AMB-2 and AMB-4 (ICU units) out of service",
    "💥 Mass casualty": "Three severe emergencies are registered at once",
}


def apply_preset(name):
    if name.startswith("🚦"):
        for a, b in ROADS:
            if "Central" in (a, b):
                sc["traffic"][edge_key(a, b)] = 3.0
    elif name.startswith("🌊"):
        for pair in [("Old Town", "Riverside"), ("Harbor", "City General"), ("South Gate", "Harbor")]:
            if edge_key(*pair) not in sc["blocked"]:
                sc["blocked"].append(edge_key(*pair))
    elif name.startswith("🏥"):
        for h in sc["hospitals"]:
            h["total_beds"] = h["occupied"] + 1
    elif name.startswith("🚑"):
        for a in sc["ambulances"]:
            if a["id"] in ("AMB-2", "AMB-4") and a["status"] == "Available":
                a["status"] = "Disabled"
    elif name.startswith("💥"):
        number = max(int(i["id"].split("-")[1]) for i in sc["incidents"])
        for k, (loc, need) in enumerate([("Central", "Trauma"), ("Market", "ICU"), ("Harbor", "Trauma")]):
            sc["incidents"].append({"id": f"INC-{number + 1 + k}", "location": loc, "severity": 5 - k // 2,
                                    "need": need, "status": "Open", "desc": "Mass casualty", "amb": "", "hospital": ""})
    log(f"Preset applied: {name}")
    notify("success", f"Preset applied: {name}")


def page_controls():
    st.subheader("Scenario controls")
    st.caption("Every change updates all pages instantly. Use the sidebar button to return to the default scenario.")
    left, right = st.columns([2, 3])
    with left:
        tab_pre, tab_traffic, tab_block, tab_cap, tab_amb = st.tabs(
            ["⚡ Presets", "🚦 Traffic", "🚧 Closures", "🏥 Capacity", "🚑 Ambulances"])
        with tab_pre:
            for name, text in PRESETS.items():
                if st.button(name, help=text, key=f"preset_{name}"):
                    apply_preset(name)
                st.caption(text)
        with tab_traffic:
            with st.form("traffic"):
                road = st.selectbox("Road", [edge_key(a, b) for a, b in ROADS], format_func=road_label)
                mult = st.slider("Traffic multiplier (1.0 = clear)", 1.0, 5.0, 1.0, 0.1)
                if st.form_submit_button("Apply traffic"):
                    if mult == 1.0:
                        sc["traffic"].pop(road, None)
                    else:
                        sc["traffic"][road] = mult
                    log(f"Traffic on {road_label(road)} set to x{mult:.1f}")
                    notify("success", f"Traffic on {road_label(road)} is now x{mult:.1f}.")
            if sc["traffic"]:
                st.dataframe(pd.DataFrame([{"Road": road_label(k), "x": v} for k, v in sc["traffic"].items()]),
                             hide_index=True)
        with tab_block:
            with st.form("blocked"):
                chosen = st.multiselect("Blocked roads", [edge_key(a, b) for a, b in ROADS], default=sc["blocked"],
                                        format_func=road_label)
                if st.form_submit_button("Apply closures"):
                    sc["blocked"] = chosen
                    log(f"{len(chosen)} road(s) blocked")
                    notify("success", f"{len(chosen)} road(s) are now blocked.")
        with tab_cap:
            with st.form("capacity"):
                beds = {h["name"]: st.number_input(f"{h['name']} total beds (occupied {h['occupied']})", 0, 30,
                                                   h["total_beds"]) for h in sc["hospitals"]}
                if st.form_submit_button("Apply capacity"):
                    for h in sc["hospitals"]:
                        h["total_beds"] = int(beds[h["name"]])
                    log("Hospital capacity changed")
                    notify("success", "Hospital capacity updated.")
        with tab_amb:
            usable = [a["id"] for a in sc["ambulances"] if a["status"] in ("Available", "Disabled")]
            with st.form("ambulances"):
                off = st.multiselect("Disabled ambulances", usable,
                                     default=[a["id"] for a in sc["ambulances"] if a["status"] == "Disabled"])
                if st.form_submit_button("Apply ambulances"):
                    for a in sc["ambulances"]:
                        if a["id"] in usable:
                            a["status"] = "Disabled" if a["id"] in off else "Available"
                    log(f"Disabled ambulances: {', '.join(off) or 'none'}")
                    notify("success", "Ambulance availability updated.")

    with right:
        prep, alloc = plan(sc)
        cut_off = unreachable_nodes(prep["adj"])
        if cut_off:
            st.warning("Cut off from the rest of the city: " + ", ".join(cut_off))
        st.markdown("**Live impact on the CSP plan**")
        etas = [v[3] for v in alloc["assignments"].values()]
        k = st.columns(4)
        k[0].metric("Assigned", f"{len(alloc['assignments'])} / {len(prep['incidents'])}")
        k[1].metric("Failed", len(alloc["failed"]))
        k[2].metric("Avg response", f"{sum(etas) / len(etas):.1f} min" if etas else "n/a")
        k[3].metric("Ambulances free", len(prep["ambulances"]))
        show_html(cv.dispatch_map_html(sc, prep["adj"], city_missions(prep, alloc), panel=False, height=560), 565)


def page_reports():
    st.subheader("Evaluation and reports")
    tab_tests, tab_routes, tab_csp, tab_strategy = st.tabs(
        ["✅ Test results", "Route comparison", "Allocation results", "Minimax vs Alpha-Beta"])

    with tab_tests:
        if st.button("▶ Run automated test suite"):
            with st.spinner("Running pytest..."):
                try:
                    proc = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q", "--tb=short", "-p", "no:cacheprovider"],
                                          cwd=ROOT, capture_output=True, text=True, timeout=300)
                    st.session_state.tests = (proc.returncode, proc.stdout + proc.stderr)
                except Exception:
                    st.session_state.tests = (1, "The test run could not be completed here. Run `python -m pytest tests -q` in a terminal.")
        if "tests" not in st.session_state:
            st.info("No test run yet in this session. Press the button to run the real test suite.")
        else:
            code, output = st.session_state.tests
            last = [ln for ln in output.strip().splitlines() if ln.strip()][-1] if output.strip() else ""
            (st.success if code == 0 else st.warning)(last or "Test run produced no output")
            st.code(output)

    prep, alloc = plan(sc)
    with tab_routes:
        rows = []
        for inc in prep["incidents"]:
            for amb in prep["ambulances"]:
                a, d = compare(prep["adj"], amb["base"], inc["location"], repeats=20)
                rows.append({"Trip": f"{amb['id']} → {inc['id']}", "A* cost": round(a["cost"], 2),
                             "Dijkstra cost": round(d["cost"], 2), "A* explored": a["explored"],
                             "Dijkstra explored": d["explored"], "A* ms": round(a["time_ms"], 4),
                             "Dijkstra ms": round(d["time_ms"], 4)})
        if not rows:
            st.info("Need at least one open emergency and one available ambulance.")
        else:
            df = pd.DataFrame(rows)
            st.dataframe(df, hide_index=True)
            fig = go.Figure()
            fig.add_bar(name="A*", x=df["Trip"], y=df["A* explored"], marker_color="#ef4444")
            fig.add_bar(name="Dijkstra", x=df["Trip"], y=df["Dijkstra explored"], marker_color="#3b82f6")
            fig.update_layout(barmode="group", yaxis_title="Explored nodes", legend=dict(orientation="h", y=1.1))
            st.plotly_chart(dark(fig, 320))
            same = (df["A* cost"] - df["Dijkstra cost"]).abs().max() < 1e-6
            (st.success if same else st.info)("A* and Dijkstra costs match on every trip." if same else "A* and Dijkstra costs differ on some trips; compare the columns above.")
            st.download_button("⬇ Download route comparison (CSV)", df.to_csv(index=False), "route_comparison.csv")

    with tab_csp:
        rows = [{"Incident": k, "Ambulance": v[0], "Hospital": v[1], "Response_min": v[3], "Total_min": v[2],
                 "Result": "assigned", "Reason": ""} for k, v in alloc["assignments"].items()]
        rows += [{"Incident": f["incident"], "Ambulance": "", "Hospital": "", "Response_min": "", "Total_min": "",
                  "Result": "failed", "Reason": f["reason"]} for f in alloc["failed"]]
        if not rows:
            st.info("No open emergencies to allocate.")
        else:
            df = pd.DataFrame(rows)
            st.dataframe(df, hide_index=True)
            st.download_button("⬇ Download allocation (CSV)", df.to_csv(index=False), "allocation.csv")

    with tab_strategy:
        world = make_world(prep)
        if not world["incidents"]:
            st.info("No open emergencies to plan for.")
        else:
            st.write("Runs both algorithms at several depths on the current scenario (can take a few seconds).")
            if st.button("▶ Run depth benchmark"):
                rows = []
                for depth in range(1, min(4, len(world["incidents"])) + 1):
                    mm, ab = minimax_decide(world, depth), alphabeta_decide(world, depth)
                    rows.append({"Depth": depth, "Minimax nodes": mm["nodes"], "Alpha-Beta nodes": ab["nodes"],
                                 "Cutoffs": ab["pruned"], "Minimax ms": round(mm["time_ms"], 2),
                                 "Alpha-Beta ms": round(ab["time_ms"], 2), "Same decision": mm["action"] == ab["action"],
                                 "Utility": round(mm["utility"], 2)})
                st.session_state.bench = pd.DataFrame(rows)
            if "bench" in st.session_state:
                df = st.session_state.bench
                st.dataframe(df, hide_index=True)
                fig = go.Figure()
                fig.add_bar(name="Minimax", x=df["Depth"], y=df["Minimax nodes"], marker_color="#3b82f6")
                fig.add_bar(name="Alpha-Beta", x=df["Depth"], y=df["Alpha-Beta nodes"], marker_color="#ef4444")
                fig.update_layout(barmode="group", xaxis_title="Depth", yaxis_title="Nodes", legend=dict(orientation="h", y=1.1))
                st.plotly_chart(dark(fig, 320))
                st.download_button("⬇ Download benchmark (CSV)", df.to_csv(index=False), "minimax_benchmark.csv")
            else:
                st.info("No benchmark run yet.")


# ------------------------------------------------------------------ main
st.sidebar.markdown("## 🚑 MediFlow")
st.sidebar.caption("Emergency medical resource allocation")
page = st.sidebar.radio("Navigation", PAGES, label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.caption(f"🔴 Open emergencies: {sum(i['status'] == 'Open' for i in sc['incidents'])}  \n"
                   f"🚑 Available ambulances: {sum(a['status'] == 'Available' for a in sc['ambulances'])}  \n"
                   f"🚧 Blocked roads: {len(sc['blocked'])}  \n"
                   f"🚦 Traffic roads: {len(sc['traffic'])}")
if st.sidebar.button("↺ Reset to default scenario"):
    st.session_state.scenario = default_scenario()
    for key in ("strategy", "bench"):
        st.session_state.pop(key, None)
    notify("success", "Scenario reset to the default.")
st.sidebar.info("Educational simulation. Not a real dispatch or medical system.")

critical_open = any(i["status"] == "Open" and i["severity"] >= 4 for i in sc["incidents"])
st.markdown(f'<div class="hdr"><span class="logo">🚑</span><div><h1>MEDIFLOW</h1><p>AI emergency operations center · fictional city simulation</p></div>'
            f'<div class="pg">{page[2:].strip()}</div><div class="stat"><span class="live"></span>SIMULATION ONLINE</div></div>'
            f'<div class="sirenbar{" on" if critical_open else ""}"></div>', unsafe_allow_html=True)
if "flash" in st.session_state:
    kind, message = st.session_state.pop("flash")
    getattr(st, kind)(message)

try:
    dict(zip(PAGES, [page_overview, page_incidents, page_map, page_routes, page_allocation,
                     page_strategy, page_controls, page_reports]))[page]()
except Exception as exc:                      # never show a traceback to the person using the dashboard
    st.session_state["_page_error"] = f"{page}: {exc!r}"      # kept for the automated tests and the server log
    print(f"[MediFlow] page '{page}' failed: {exc!r}", file=sys.stderr)
    st.info("This page could not be drawn for the current scenario. Use **Reset to default scenario** in the sidebar, "
            "or change the last setting you touched.")

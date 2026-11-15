"""Plotly figures used by the MediFlow GUI.

make_map         - the city road network (roads, hospitals, ambulances, emergencies, routes)
make_missions    - turns the CSP plan into ambulance trips with timings
build_animation  - the map with ambulances that drive their routes over time
gantt_figure     - timeline of every trip
sankey_figure    - emergency -> ambulance -> hospital flow of the CSP plan
tree_figure      - top of the Minimax decision tree
"""
import plotly.graph_objects as go

from mediflow.data import NODES, ROADS, HOSPITAL_NODES, edge_key, base_cost
from mediflow.planner import free_beds
from mediflow.routing import astar
from mediflow.strategy import adverse_breakdown

BG = "#0b1424"          # map background
TEXT = "#cbd5e1"        # light text on dark background
ROUTE_COLORS = ["#38bdf8", "#4ade80", "#c084fc", "#fb923c", "#f472b6", "#facc15"]


def _layout(fig, height):
    fig.update_layout(
        height=height, margin=dict(l=5, r=5, t=5, b=5), paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(color=TEXT), xaxis=dict(visible=False, range=[-0.6, 10.6]),
        yaxis=dict(visible=False, range=[0.4, 11], scaleanchor="x"),
        legend=dict(orientation="h", y=1.0, x=0, bgcolor="rgba(0,0,0,0.35)", font=dict(size=11)))


def _add_units(fig, xs, ys, emoji, color, name, hover, labels, label_pos, size=26):
    """Draw a group of map icons: a colored disc, an emoji, and a small text label."""
    if not xs:
        return
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers+text", name=name, text=[emoji] * len(xs),
                             textfont=dict(size=15), textposition="middle center", hoverinfo="text",
                             hovertext=hover, marker=dict(size=size, color=color, opacity=0.95,
                                                          line=dict(color="white", width=1.5))))
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="text", text=labels, textposition=label_pos, showlegend=False,
                             hoverinfo="skip", textfont=dict(size=10, color="white")))


def draw_roads(fig, sc):
    """Roads: grey = clear, orange = traffic, red dotted = blocked."""
    shown, mid_x, mid_y, mid_text = set(), [], [], []
    for a, b in ROADS:
        key = edge_key(a, b)
        (x0, y0), (x1, y1) = NODES[a], NODES[b]
        mult = sc["traffic"].get(key, 1.0)
        if key in sc["blocked"]:
            label, color, dash, width = "Blocked road", "#ef4444", "dot", 4
        elif mult >= 2.0:
            label, color, dash, width = "Heavy traffic", "#f97316", "solid", 5
        elif mult > 1.0:
            label, color, dash, width = "Light traffic", "#fbbf24", "solid", 4
        else:
            label, color, dash, width = "Clear road", "#475569", "solid", 4
        fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode="lines", name=label, legendgroup=label,
                                 showlegend=label not in shown, hoverinfo="skip",
                                 line=dict(color=color, width=width, dash=dash)))
        shown.add(label)
        mid_x.append((x0 + x1) / 2)
        mid_y.append((y0 + y1) / 2)
        info = "BLOCKED" if key in sc["blocked"] else f"{base_cost(a, b) * max(1.0, mult):.1f} min (traffic x{mult:.1f})"
        mid_text.append(f"{a} ↔ {b}: {info}")
    fig.add_trace(go.Scatter(x=mid_x, y=mid_y, mode="markers", showlegend=False, hoverinfo="text", text=mid_text,
                             marker=dict(size=16, color="rgba(0,0,0,0)")))


def draw_places(fig, sc):
    """Intersections and hospitals."""
    inter = [n for n in NODES if n not in HOSPITAL_NODES]
    fig.add_trace(go.Scatter(x=[NODES[n][0] for n in inter], y=[NODES[n][1] for n in inter],
                             mode="markers+text", name="Intersection", text=inter, textposition="bottom center",
                             textfont=dict(size=10, color=TEXT), hoverinfo="skip",
                             marker=dict(size=11, color="#94a3b8", line=dict(color=BG, width=2))))
    hs = sc["hospitals"]
    _add_units(fig, [NODES[h["name"]][0] for h in hs], [NODES[h["name"]][1] for h in hs], "🏥", "#0d9488",
               "Hospital",
               [f"{h['name']}: {free_beds(h)} free of {h['total_beds']} beds, offers {', '.join(h['services'])}"
                for h in hs], [h["name"] for h in hs], "bottom center", size=34)


def make_map(sc, routes=(), explored=None, units=True, height=620):
    """Static map. routes = [{route, name, color, dash}], explored = {order, name, color}."""
    fig = go.Figure()
    draw_roads(fig, sc)
    for r in routes:                                   # glow + line
        if len(r["route"]) > 1:
            xs, ys = [NODES[n][0] for n in r["route"]], [NODES[n][1] for n in r["route"]]
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", showlegend=False, hoverinfo="skip",
                                     line=dict(color=r["color"], width=14), opacity=0.25))
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name=r["name"], hoverinfo="name",
                                     line=dict(color=r["color"], width=5, dash=r.get("dash", "solid"))))
    if explored:                                       # numbered circles = expansion order
        order = explored["order"]
        fig.add_trace(go.Scatter(x=[NODES[n][0] for n in order], y=[NODES[n][1] for n in order],
                                 mode="markers+text", name=explored["name"], text=[str(i + 1) for i in range(len(order))],
                                 textfont=dict(color="white", size=12), hoverinfo="text",
                                 hovertext=[f"#{i + 1}: {n}" for i, n in enumerate(order)],
                                 marker=dict(size=30, color=explored["color"], opacity=0.55,
                                             line=dict(color=explored["color"], width=2))))
    draw_places(fig, sc)
    if units:
        colors = {"Available": "#2563eb", "Busy": "#d97706", "Disabled": "#64748b"}
        for status in colors:
            g = [a for a in sc["ambulances"] if a["status"] == status]
            _add_units(fig, [NODES[a["base"]][0] + 0.3 for a in g], [NODES[a["base"]][1] - 0.35 for a in g], "🚑",
                       colors[status], f"Ambulance ({status.lower()})",
                       [f"{a['id']} at {a['base']} - {', '.join(a['equipment'])}" for a in g],
                       [a["id"] for a in g], "bottom center", size=26)
        for status, color in [("Open", "#dc2626"), ("Dispatched", "#f59e0b")]:
            g = [i for i in sc["incidents"] if i["status"] == status]
            _add_units(fig, [NODES[i["location"]][0] - 0.3 for i in g], [NODES[i["location"]][1] + 0.35 for i in g],
                       "🚨", color, f"Emergency ({status.lower()})",
                       [f"{i['id']}: {i['desc']} - severity {i['severity']}, needs {i['need']}" for i in g],
                       [f"{i['id']} (sev {i['severity']})" for i in g], "top center", size=26)
    _layout(fig, height)
    return fig


# ------------------------------------------------------------ animation
def make_missions(prep, alloc):
    """One mission per CSP assignment: path = base -> scene -> hospital, with the
    cumulative travel time (minutes) at every node of the path."""
    adj = prep["adj"]
    ambs = {a["id"]: a for a in prep["ambulances"]}
    incs = {i["id"]: i for i in prep["incidents"]}
    missions = []
    for inc_id, (amb, hosp, _, _) in alloc["assignments"].items():
        to_scene = astar(adj, ambs[amb]["base"], incs[inc_id]["location"])["route"]
        to_hosp = astar(adj, incs[inc_id]["location"], hosp)["route"]
        path = to_scene + to_hosp[1:]
        times = [0.0]
        for p, q in zip(path, path[1:]):
            times.append(times[-1] + dict(adj[p])[q])
        missions.append({"inc": inc_id, "amb": amb, "hosp": hosp, "severity": incs[inc_id]["severity"],
                         "location": incs[inc_id]["location"], "base": ambs[amb]["base"], "path": path,
                         "times": times, "scene_time": times[len(to_scene) - 1], "total": times[-1]})
    return missions


def _position(m, t):
    """Where the ambulance is at time t (linear interpolation along the path)."""
    path, times = m["path"], m["times"]
    if t >= times[-1]:
        return NODES[path[-1]]
    for i in range(len(path) - 1):
        if times[i] <= t < times[i + 1]:
            f = (t - times[i]) / (times[i + 1] - times[i])
            (x0, y0), (x1, y1) = NODES[path[i]], NODES[path[i + 1]]
            return (x0 + f * (x1 - x0), y0 + f * (y1 - y0))
    return NODES[path[0]]


def _trail(m, t):
    """Points the ambulance has already driven through."""
    pts = [NODES[n] for n, tt in zip(m["path"], m["times"]) if tt <= t]
    pts.append(_position(m, t))
    return pts


def _frame_data(sc, prep, missions, t):
    """Positions/colors of all moving things at time t."""
    tx, ty, ax, ay, atext, acol, ahover = [], [], [], [], [], [], []
    state = {}
    for m in missions:
        pts = _trail(m, t)
        tx += [p[0] for p in pts] + [None]
        ty += [p[1] for p in pts] + [None]
        x, y = _position(m, t)
        if t < m["scene_time"]:
            phase, col, inc_state = "driving to the scene", "#3b82f6", ("#dc2626", "waiting for help")
        elif t < m["total"]:
            phase, col, inc_state = f"carrying patient to {m['hosp']}", "#f59e0b", ("#f59e0b", "picked up")
        else:
            phase, col, inc_state = f"arrived at {m['hosp']}", "#22c55e", ("#22c55e", "delivered")
        state[m["inc"]] = inc_state
        ax.append(x); ay.append(y); acol.append(col)
        atext.append("🚑")
        ahover.append(f"{m['amb']} ({m['inc']}): {phase}")
    ix, iy, icol, ihover = [], [], [], []
    for i in prep["incidents"]:
        col, txt = state.get(i["id"], ("#7f1d1d", "NO AMBULANCE ASSIGNED"))
        ix.append(NODES[i["location"]][0]); iy.append(NODES[i["location"]][1])
        icol.append(col)
        ihover.append(f"{i['id']} (severity {i['severity']}): {txt}")
    return tx, ty, ax, ay, atext, acol, ahover, ix, iy, icol, ihover


def build_animation(sc, prep, alloc, missions, speed_ms=120, steps=70):
    """Map with ambulances that really drive along their A* routes (press Play)."""
    fig = make_map(sc, units=False)
    horizon = max(m["total"] for m in missions) + 1.0
    times = [horizon * k / steps for k in range(steps + 1)]
    first = len(fig.data)                                    # index of the first moving trace

    def traces(t):
        tx, ty, ax, ay, atext, acol, ahover, ix, iy, icol, ihover = _frame_data(sc, prep, missions, t)
        return [
            go.Scatter(x=tx, y=ty, mode="lines", name="Driven path", hoverinfo="skip",
                       line=dict(color="#38bdf8", width=6)),
            go.Scatter(x=ix, y=iy, mode="markers+text", name="Emergency", text=["🚨"] * len(ix),
                       textfont=dict(size=15), hoverinfo="text", hovertext=ihover,
                       marker=dict(size=28, color=icol, line=dict(color="white", width=1.5))),
            go.Scatter(x=ax, y=ay, mode="markers+text", name="Ambulance", text=atext, textfont=dict(size=16),
                       hoverinfo="text", hovertext=ahover,
                       marker=dict(size=30, color=acol, line=dict(color="white", width=2))),
        ]

    for tr in traces(0.0):
        fig.add_trace(tr)
    fig.frames = [go.Frame(data=traces(t), traces=[first, first + 1, first + 2], name=f"{t:.1f}") for t in times]
    fig.update_layout(
        updatemenus=[dict(type="buttons", showactive=False, x=0.0, y=-0.02, xanchor="left", yanchor="top",
                          bgcolor="#1e293b", font=dict(color="white"), buttons=[
            dict(label="▶ Play", method="animate",
                 args=[None, dict(frame=dict(duration=speed_ms, redraw=True), fromcurrent=True,
                                  transition=dict(duration=0))]),
            dict(label="⏸ Pause", method="animate",
                 args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate",
                                    transition=dict(duration=0))])])],
        sliders=[dict(x=0.18, len=0.82, y=-0.02, yanchor="top", pad=dict(t=0, b=0),
                      currentvalue=dict(prefix="Simulated time: ", suffix=" min", font=dict(color="white")),
                      font=dict(color="rgba(0,0,0,0)", size=1), tickcolor="rgba(0,0,0,0)",
                      steps=[dict(method="animate", label=f"{t:.1f}",
                                  args=[[f"{t:.1f}"], dict(mode="immediate", frame=dict(duration=0, redraw=True),
                                                           transition=dict(duration=0))]) for t in times])])
    fig.update_layout(height=680, margin=dict(l=5, r=5, t=5, b=70))
    return fig


def gantt_figure(missions):
    """Horizontal timeline: time to reach the scene, then time to reach the hospital."""
    fig = go.Figure()
    fig.add_bar(y=[m["amb"] + " → " + m["inc"] for m in missions], x=[m["scene_time"] for m in missions],
                base=[0] * len(missions), orientation="h", name="Driving to scene", marker_color="#3b82f6")
    fig.add_bar(y=[m["amb"] + " → " + m["inc"] for m in missions], x=[m["total"] - m["scene_time"] for m in missions],
                base=[m["scene_time"] for m in missions], orientation="h", name="Patient to hospital",
                marker_color="#f59e0b")
    fig.update_layout(barmode="overlay", height=60 + 42 * len(missions), margin=dict(l=5, r=5, t=5, b=30),
                      xaxis_title="Minutes from dispatch", yaxis=dict(autorange="reversed"),
                      legend=dict(orientation="h", y=1.15))
    return fig


def sankey_figure(alloc, incidents):
    """Flow emergency -> ambulance -> hospital for the CSP plan."""
    info = {i["id"]: i for i in incidents}
    labels, index = [], {}

    def node(label):
        if label not in index:
            index[label] = len(labels)
            labels.append(label)
        return index[label]

    src, dst, val, col = [], [], [], []
    for inc_id, (amb, hosp, _, _) in alloc["assignments"].items():
        i = info[inc_id]
        a = node(f"{inc_id} · {i['need']} · sev {i['severity']}")
        b = node(amb)
        c = node(hosp)
        shade = "rgba(239,68,68,0.55)" if i["severity"] >= 4 else "rgba(56,189,248,0.5)"
        src += [a, b]; dst += [b, c]; val += [1, 1]; col += [shade, shade]
    for f in alloc["failed"]:                      # unserved incidents appear with no flow
        node(f"{f['incident']} · UNSERVED")
    fig = go.Figure(go.Sankey(
        node=dict(label=labels, pad=18, thickness=18,
                  color=["#ef4444" if "UNSERVED" in l else "#475569" for l in labels]),
        link=dict(source=src, target=dst, value=val, color=col)))
    fig.update_layout(height=380, margin=dict(l=5, r=5, t=10, b=10), paper_bgcolor=BG, font=dict(color=TEXT))
    return fig


def tree_figure(world, depth, mm):
    """Top of the Minimax tree: root (MAX) -> first dispatch -> adversary replies (MIN)."""
    plans = sorted(mm["values"], key=lambda k: -mm["values"][k])
    fig = go.Figure()
    leaf_y, plan_pos, rows = 0, {}, []
    for inc in plans:
        replies = adverse_breakdown(world, depth, inc)
        ys = []
        for name, value in replies.items():
            ys.append(leaf_y)
            rows.append((inc, name, value, leaf_y))
            leaf_y -= 1
        if not replies:
            ys.append(leaf_y)
            leaf_y -= 1
        plan_pos[inc] = sum(ys) / len(ys)
        leaf_y -= 0.6
    root_y = sum(plan_pos.values()) / len(plan_pos)
    for inc in plans:                                  # root -> plan lines
        good = inc == mm["action"]
        fig.add_trace(go.Scatter(x=[0, 1], y=[root_y, plan_pos[inc]], mode="lines", showlegend=False, hoverinfo="skip",
                                 line=dict(color="#22c55e" if good else "#475569", width=4 if good else 2)))
    for inc, name, value, y in rows:                   # plan -> adversary lines
        worst = abs(value - mm["values"][inc]) < 1e-9
        fig.add_trace(go.Scatter(x=[1, 2], y=[plan_pos[inc], y], mode="lines", showlegend=False, hoverinfo="skip",
                                 line=dict(color="#ef4444" if worst else "#334155", width=3 if worst else 1.5)))
    fig.add_trace(go.Scatter(x=[0], y=[root_y], mode="markers+text", text=["MAX: choose first dispatch"],
                             textposition="middle left", showlegend=False, hoverinfo="skip",
                             marker=dict(size=22, symbol="square", color="#3b82f6")))
    fig.add_trace(go.Scatter(x=[1] * len(plans), y=[plan_pos[p] for p in plans], mode="markers+text",
                             text=[f"{p}<br>worst case {mm['values'][p]:.1f}" for p in plans],
                             textposition="top center", showlegend=False, hoverinfo="skip",
                             marker=dict(size=20, symbol="diamond",
                                         color=["#22c55e" if p == mm["action"] else "#64748b" for p in plans])))
    fig.add_trace(go.Scatter(x=[2] * len(rows), y=[r[3] for r in rows], mode="markers+text",
                             text=[f"{r[1]}: {r[2]:.1f}" for r in rows], textposition="middle right",
                             showlegend=False, hoverinfo="skip", textfont=dict(size=10),
                             marker=dict(size=12, color="#f87171")))
    fig.update_layout(height=max(380, 28 * len(rows) + 120), margin=dict(l=5, r=5, t=5, b=5), paper_bgcolor=BG,
                      plot_bgcolor=BG, font=dict(color=TEXT), xaxis=dict(visible=False, range=[-1.2, 3.6]),
                      yaxis=dict(visible=False))
    return fig

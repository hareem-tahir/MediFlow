"""HTML/SVG views for the MediFlow GUI (no extra dependencies, no map tokens).

dispatch_map_html - the city map: roads, traffic, closures, hospitals, incidents, moving
                    ambulances with flashing sirens, selected and alternative routes
search_html       - A* and Dijkstra side by side, stepping through the real search trace
tree_html         - Minimax / Alpha-Beta decision trees (selected branch, pruned branches)
csp_cards_html    - allocation cards with the constraints that were checked

All numbers come from the algorithm modules; the JavaScript only plays them back.
Each *_html function returns a complete HTML document for streamlit.components.v1.html.
"""
import html
import json
import math
from functools import lru_cache

from mediflow import city_assets as A
from mediflow.data import NODES, ROADS, HOSPITAL_NODES, edge_key, base_cost
from mediflow.routing import astar, alternative_routes, heuristic

COLORS = ["#38bdf8", "#4ade80", "#c084fc", "#fb923c", "#f472b6", "#facc15"]
SEV_COLOR = {5: "#ef4444", 4: "#f97316", 3: "#eab308", 2: "#84cc16", 1: "#22c55e"}
W, H = 1000, 760


def _road_cost(sc, a, b):
    """Travel time of one road in this scenario (minutes, traffic included)."""
    return base_cost(a, b) * max(1.0, sc["traffic"].get(edge_key(a, b), 1.0))


def px(name):
    """Map position of a place in SVG pixels (north is up)."""
    x, y = NODES[name]
    return round(30 + x * 100, 1), round(700 - (y - 1) * 70, 1)


def _json(data):
    return json.dumps(data).replace("</", "<\\/")


def _page(body, js, data, extra_css=""):
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{A.CSS}{extra_css}</style></head><body>"
            f"{body}<script id='data' type='application/json'>{_json(data)}</script><script>{js}</script></body></html>")


# ----------------------------------------------------------------- static city art
def _seg_dist(p, a, b):
    (x, y), (x1, y1), (x2, y2) = p, a, b
    dx, dy = x2 - x1, y2 - y1
    t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))


@lru_cache(maxsize=1)
def _blocks_svg():
    """City blocks (buildings, a park) placed in the gaps between the roads."""
    segs = [(px(a), px(b)) for a, b in ROADS]
    pts = [px(n) for n in NODES]
    pal = ["#101b33", "#13203b", "#0f1a30", "#15233f"]
    out = []
    for gx in range(14, W - 40, 56):
        for gy in range(14, 676, 56):
            c = (gx + 22, gy + 22)
            if min(_seg_dist(c, a, b) for a, b in segs) < 42 or min(math.hypot(c[0] - p[0], c[1] - p[1]) for p in pts) < 62:
                continue
            park = math.hypot(c[0] - 430, c[1] - 300) < 74
            fill = "#0f2a25" if park else pal[((gx * 7 + gy * 3) // 56) % 4]
            stroke = "#14453a" if park else "#1a2a4a"
            out.append(f'<rect x="{gx}" y="{gy}" width="44" height="44" rx="6" fill="{fill}" stroke="{stroke}"/>')
    out.append('<text x="430" y="304" text-anchor="middle" font-size="11" fill="#2f6b58" font-weight="700" letter-spacing="2">PARK</text>')
    sea = ('<path d="M0 692 Q125 672 250 692 T500 692 T750 692 T1000 692 L1000 760 L0 760Z" fill="url(#sea)"/>'
           '<path d="M0 704 Q125 686 250 704 T500 704 T750 704 T1000 704" fill="none" stroke="#1c5f8f" stroke-width="1.5" opacity=".6"/>')
    return sea + "".join(out)


def _roads_svg(sc, flow=True):
    """Every road: dark casing, asphalt, lane dashes, plus traffic colour or closure hatching."""
    cased, body, extra = [], [], []
    for a, b in ROADS:
        key = edge_key(a, b)
        (x1, y1), (x2, y2) = px(a), px(b)
        ln = f'x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"'
        mult = sc["traffic"].get(key, 1.0)
        cost = base_cost(a, b) * max(1.0, mult)
        cased.append(f'<line class="road-case" {ln}/>')
        if key in sc["blocked"]:
            tip = f"{a} ↔ {b}: ROAD BLOCKED"
            body.append(f'<g data-edge="{a}|{b}"><line class="road-body" {ln}/><line class="road-traffic" {ln} stroke="url(#hatch)"/>'
                        f'<title>{html.escape(tip)}</title></g>')
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            extra.append(f'<g transform="translate({mx},{my})"><circle r="15" fill="#ef4444" stroke="#fff" stroke-width="2.5"/>'
                         f'<rect x="-9" y="-3.2" width="18" height="6.4" rx="1.5" fill="#fff"/><title>{html.escape(tip)}</title></g>'
                         f'<text x="{mx}" y="{my + 31}" text-anchor="middle" class="tag" fill="#fca5a5">CLOSED</text>')
        else:
            tip = f"{a} ↔ {b}: {cost:.1f} min" + (f" (traffic ×{mult:.1f})" if mult > 1 else " (clear)")
            col = None if mult <= 1 else ("#f59e0b" if mult < 2 else "#ea580c" if mult < 3.5 else "#dc2626")
            inner = f'<line class="road-body" {ln}/>'
            if col:
                inner += f'<line class="road-traffic" {ln} stroke="{col}"/>'
                if flow:
                    inner += f'<line class="traffic-flow" {ln}/>'
            inner += f'<line class="road-line" {ln}/><title>{html.escape(tip)}</title>'
            body.append(f'<g data-edge="{a}|{b}">{inner}</g>')
            if col:
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                extra.append(f'<g transform="translate({mx},{my})"><rect x="-19" y="-10" width="38" height="20" rx="10" fill="{col}" stroke="#0a1020" stroke-width="2"/>'
                             f'<text y="4.5" text-anchor="middle" font-size="11" font-weight="800" fill="#fff">×{mult:.1f}</text><title>{html.escape(tip)}</title></g>')
    return "".join(cased) + "".join(body) + "".join(extra)


def _places_svg(sc, show_hospitals=True, node_names=True):
    """Intersections (named) and hospitals (building icon with bed-capacity bar)."""
    out = []
    hosp = {h["name"]: h for h in sc["hospitals"]}
    for n in NODES:
        x, y = px(n)
        if n in hosp:
            continue
        out.append(f'<g data-n="{n}"><circle class="nd" cx="{x}" cy="{y}" r="12"/>'
                   + (f'<text class="nlabel" x="{x}" y="{y + 27}" text-anchor="middle">{n}</text>' if node_names else "") + "</g>")
    for n, h in hosp.items():
        x, y = px(n)
        free = max(0, h["total_beds"] - h["occupied"])
        ratio = min(1, h["occupied"] / h["total_beds"]) if h["total_beds"] else 1
        col = "#22c55e" if ratio < .6 else "#f59e0b" if ratio < .85 else "#ef4444"
        full = free == 0
        tip = (f"{n}\nServices: {', '.join(h['services'])}\nBeds: {free} free of {h['total_beds']} ({h['occupied']} occupied)"
               + ("\nFULL – cannot accept patients" if full else ""))
        beds_txt = "FULL" if full else f"{free} bed{'s' if free != 1 else ''} free"
        detail = ""
        if show_hospitals:      # full card: capacity bar + free beds (hidden in the compact search view)
            detail = (f'<rect x="-30" y="42" width="60" height="8" rx="4" fill="#0a1020" stroke="#2a3a5e"/>'
                      f'<rect x="-30" y="42" width="{60 * ratio:.1f}" height="8" rx="4" fill="{col}"/>'
                      f'<text class="tag" y="80" text-anchor="middle" fill="{"#fca5a5" if full else "#99f6e4"}">'
                      f'{beds_txt}</text>')
        out.append(
            f'<g data-n="{n}" transform="translate({x},{y})"><circle class="nd" r="36" fill="#0b2a2e" stroke="{"#ef4444" if full else "#2dd4bf"}" stroke-width="3"/>'
            f'<rect x="-23" y="-23" width="46" height="46" rx="10" fill="{"#7f1d1d" if full else "#0f766e"}" stroke="#ccfbf1" stroke-width="2"/>'
            f'<rect x="-5.5" y="-15" width="11" height="30" rx="2" fill="#fff"/><rect x="-15" y="-5.5" width="30" height="11" rx="2" fill="#fff"/>'
            f'{detail}<text class="nlabel" y="{66 if show_hospitals else 54}" text-anchor="middle">{n}</text>'
            f'<title>{html.escape(tip)}</title></g>')
    return "".join(out)


def city_svg(sc, **kw):
    return (f'<rect width="{W}" height="{H}" fill="#0a1020"/>{_blocks_svg()}{_roads_svg(sc, kw.get("flow", True))}'
            f'{_places_svg(sc, kw.get("hospitals", True), kw.get("names", True))}')


# -------------------------------------------------------------------- missions
def build_missions(adj, sc, triples, status, color_offset=0):
    """One mission per (incident, ambulance, hospital): the real A* route base -> scene -> hospital,
    cumulative minutes at every node, and the cheapest alternative routes to the scene."""
    ambs = {a["id"]: a for a in sc["ambulances"]}
    incs = {i["id"]: i for i in sc["incidents"]}
    out = []
    for inc_id, amb_id, hosp in triples:
        a, i = ambs[amb_id], incs[inc_id]
        r1, r2 = astar(adj, a["base"], i["location"]), astar(adj, i["location"], hosp)
        if not r1["route"] or not r2["route"]:
            continue
        path = r1["route"] + r2["route"][1:]
        times = [0.0]
        for p, q in zip(path, path[1:]):
            times.append(times[-1] + dict(adj[p])[q])
        alts = [{"pts": [px(n) for n in r["route"]], "names": r["route"], "cost": r["cost"], "extra": r["extra"]}
                for r in alternative_routes(adj, a["base"], i["location"], 2)]
        out.append({"inc": inc_id, "amb": amb_id, "hosp": hosp, "sev": i["severity"], "loc": i["location"],
                    "names": path, "pts": [px(n) for n in path], "times": times, "scene_idx": len(r1["route"]) - 1,
                    "scene_time": times[len(r1["route"]) - 1], "total": times[-1], "eta": r1["cost"],
                    "color": COLORS[(color_offset + len(out)) % len(COLORS)], "status": status, "alts": alts})
    return out


def committed_triples(sc):
    """Dispatches already committed in the scenario (status Dispatched)."""
    return [(i["id"], i["amb"], i["hospital"]) for i in sc["incidents"]
            if i["status"] == "Dispatched" and i["amb"] and i["hospital"]]


# ------------------------------------------------------------------ dispatch map
def _legend():
    return ('<div class="legend">'
            '<span><i class="sw" style="background:#34435f"></i>Clear road</span>'
            '<span><i class="sw" style="background:#f59e0b"></i>Light traffic</span>'
            '<span><i class="sw" style="background:#ea580c"></i>Heavy traffic</span>'
            '<span><i class="sw" style="background:repeating-linear-gradient(45deg,#ef4444 0 4px,#7f1d1d 4px 8px)"></i>Blocked road</span>'
            '<span><i class="sw" style="background:#38bdf8"></i>Selected route</span>'
            '<span><i class="sw" style="background:repeating-linear-gradient(90deg,#9fb3d6 0 3px,transparent 3px 8px)"></i>Alternative route</span>'
            '<span><i class="dot" style="background:#ef4444"></i>Incident (sev 5→1: red→green)</span>'
            '<span><i class="dot" style="background:#0f766e"></i>Hospital</span></div>')


def dispatch_map_html(sc, adj, missions, panel=True, height=740):
    """The centrepiece map. missions come from build_missions (planned + committed)."""
    by_amb = {m["amb"]: n for n, m in enumerate(missions)}
    by_inc = {m["inc"]: n for n, m in enumerate(missions)}
    horizon = (max(m["total"] for m in missions) + 0.8) if missions else 0.0
    data = {
        "missions": missions, "horizon": horizon,
        "ambs": [{"id": a["id"], "equip": a["equipment"], "status": a["status"], "base": a["base"],
                  "pos": px(a["base"]), "mission": by_amb.get(a["id"], -1)} for a in sc["ambulances"]],
        "incs": [{"id": i["id"], "loc": i["location"], "pos": px(i["location"]), "sev": i["severity"], "need": i["need"],
                  "desc": i["desc"], "status": i["status"], "mission": by_inc.get(i["id"], -1)}
                 for i in sc["incidents"] if i["status"] != "Resolved"],
    }
    cards = ""
    if panel:
        for a in sc["ambulances"]:
            m = by_amb.get(a["id"], -1)
            mm = missions[m] if m >= 0 else None
            col = mm["color"] if mm else "#475569"
            cards += (f'<div class="card" id="c-{a["id"]}" data-m="{m}" style="--c:{col}">'
                      f'<svg class="ic amb{" off" if a["status"] == "Disabled" else ""}" width="62" height="42" viewBox="-30 -28 66 56"></svg>'
                      f'<div class="hd"><b>{a["id"]}</b><span class="badge b-ok">AVAILABLE</span></div>'
                      f'<div class="chips">{"".join(f"<span class=chip>{e}</span>" for e in a["equipment"])}</div>'
                      f'<div class="kv" style="grid-column:1/3"><i>📍 Location</i><span class="lo">{a["base"]} (base)</span></div>'
                      f'<div class="kv" style="grid-column:1/3"><i>🚨 Incident</i><span>{(mm["inc"] + " · " + mm["loc"]) if mm else "— none"}</span></div>'
                      f'<div class="kv" style="grid-column:1/3"><i>🏥 Hospital</i><span>{mm["hosp"] if mm else "— none"}</span></div>'
                      f'<div class="kv" style="grid-column:1/3"><i>🛣 Route</i><span class="rt">…</span></div></div>')
    side = (f'<div class="panel"><div class="box"><h4>Ambulance fleet</h4>{cards}</div>'
            '<div class="box"><h4>Dispatch log</h4><div class="feed" id="feed"></div></div></div>') if panel else ""
    body = (f'<div class="app"><div class="mapcol"><div class="mapwrap">'
            f'<svg class="city" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet">{A.DEFS}{city_svg(sc)}'
            '<g id="l-alt"></g><g id="l-route"></g><g id="l-inc"></g><g id="l-amb"></g>'
            f'<rect width="{W}" height="{H}" fill="url(#vig)" pointer-events="none"/></svg>'
            '<div class="hud" id="hud"><div class="beacon"><i class="r"></i><i class="b"></i></div>'
            '<div><b id="hud-t">STANDBY</b><small id="hud-s"></small></div></div>'
            f'<div class="clock"><b id="clk">T+ 0.0 min</b><small>SIMULATED CLOCK</small></div>{_legend()}</div>'
            '<div class="bar"><button class="go" id="btn-run">🚨 Run dispatch</button><button id="btn-reset">⟲ Reset</button>'
            '<input type="range" id="scrub" min="0" max="1" step="0.05" value="0"><select id="spd">'
            '<option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="2">2×</option><option value="4">4×</option></select>'
            '<label class="tg"><input type="checkbox" id="tg-alt" checked>Alternative routes</label></div></div>'
            f'{side}</div>')
    if not panel:   # keep the JS happy when the side panel is absent
        body += '<div id="feed" style="display:none"></div>'
    return _page(body, A.DISPATCH_JS, data)


# --------------------------------------------------------------- search stepper
def search_html(sc, start, goal, a_res, d_res, a_stats=None, d_stats=None):
    """A* (left) and Dijkstra (right) on the same graph, stepping through the real trace.
    a_res / d_res must come from astar(..., trace=True) / dijkstra(..., trace=True)."""
    algos = []
    for key, name, res, st in (("astar", "A*", a_res, a_stats), ("dijkstra", "Dijkstra", d_res, d_stats)):
        hv = {n: round(heuristic(n, goal), 2) for n in NODES} if key == "astar" else {}
        legs = [round(_road_cost(sc, p, q), 2) for p, q in zip(res["route"], res["route"][1:])]
        algos.append({"key": key, "name": name, "steps": res["trace"], "route": res["route"], "cost": res["cost"],
                      "explored": res["explored"], "time_ms": (st or res).get("time_ms", 0.0), "h": hv, "legs": legs})
    roads = [{"a": a, "b": b, "cost": round(_road_cost(sc, a, b), 1), "mult": sc["traffic"].get(edge_key(a, b), 1.0)}
             for a, b in ROADS if edge_key(a, b) not in sc["blocked"]]
    panes = ""
    for al in algos:
        panes += (f'<div class="pane" id="p-{al["key"]}"><div class="ph"><b>{al["name"]}</b><span class="badge" id="st-{al["key"]}">READY</span></div>'
                  f'<svg class="city" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet">{A.DEFS}'
                  f'{city_svg(sc, flow=False, hospitals=False)}<g class="ov"></g></svg>'
                  f'<div class="info" id="in-{al["key"]}"></div></div>')
    data = {"algos": algos, "start": start, "goal": goal, "pos": {n: px(n) for n in NODES}, "hosp": HOSPITAL_NODES,
            "roads": roads, "blocked": [list(b) for b in sc["blocked"]]}
    body = (f'<div class="sapp"><div class="bar"><button class="go" id="s-play">▶ Play search</button><button id="s-back">◀ Step</button>'
            '<button id="s-fwd">Step ▶</button><button id="s-reset">⟲ Reset</button><input type="range" id="s-scrub" min="0" max="1" step="1" value="0">'
            '<select id="s-spd"><option value="1100">Slow</option><option value="650" selected>Normal</option><option value="250">Fast</option></select>'
            '<b id="s-step" style="min-width:90px;text-align:right"></b></div>'
            f'<div class="panes">{panes}</div>'
            '<div class="key"><span><b>Number on a road</b> = travel time in minutes</span>'
            '<span><b>g</b> = cost so far</span><span><b>h</b> = straight-line estimate to the goal (A* only)</span><span><b>f = g + h</b></span>'
            '<span><i class="dot" style="background:#3b82f6"></i>Explored</span>'
            '<span><i class="dot" style="background:#f59e0b"></i>Frontier (waiting)</span><span><i class="dot" style="background:#fff"></i>Expanding now</span>'
            '<span><i class="sw" style="background:#38bdf8"></i>Search tree</span><span><i class="sw" style="background:#22c55e"></i>Final route</span>'
            '<span><i class="sw" style="background:repeating-linear-gradient(45deg,#ef4444 0 4px,#7f1d1d 4px 8px)"></i>Blocked road</span></div></div>')
    return _page(body, A.SEARCH_JS, data, A.SEARCH_CSS)


# --------------------------------------------------------------- decision trees
def _tree_svg(tree, other=None, title=""):
    """Render one decision tree. `other` (the Alpha-Beta tree) marks branches it never evaluates."""
    plans = tree["plans"]
    rows = sum(max(1, len(p["children"])) for p in plans)
    gap, row = 22, 30
    h = rows * row + gap * len(plans) + 70
    pruned_in_other = set()
    if other:
        for p in other["plans"]:
            for c in p["children"]:
                if c["pruned"]:
                    pruned_in_other.add((p["inc"], c["name"]))
    xr, xp, xc = 60, 300, 560
    y, pos = 52, []
    for p in plans:
        n = max(1, len(p["children"]))
        ys = [y + k * row for k in range(n)]
        pos.append((sum(ys) / n, ys))
        y += n * row + gap
    ry = sum(py for py, _ in pos) / len(pos)
    s = [f'<svg viewBox="0 0 1000 {h}" width="100%" style="display:block">']
    best = tree["action"]
    edges, nodes = [], []
    for p, (py, ys) in zip(plans, pos):
        win = p["inc"] == best
        edges.append(f'<path d="M{xr},{ry} C{(xr + xp) / 2},{ry} {(xr + xp) / 2},{py} {xp},{py}" fill="none" '
                     f'stroke="{"#22c55e" if win else "#3a4a6b"}" stroke-width="{5 if win else 2}" class="seq" data-seq="{p["seq"]}"/>')
        trip = p["trip"]
        label = (f'Dispatch {p["inc"]} · {trip["amb"]} → {trip["hospital"]}' if trip else f'{p["inc"]} cannot be served')
        val = f'{"≤ " if p["cut"] else ""}{p["value"]:.1f}'
        nodes.append(
            f'<g class="seq" data-seq="{p["seq"]}"><path d="M{xp},{py - 15} L{xp + 15},{py} L{xp},{py + 15} L{xp - 15},{py} Z" '
            f'fill="{"#16a34a" if win else "#334155"}" stroke="#e2e8f0" stroke-width="{2.5 if win else 1.2}"/>'
            f'<text class="th" x="{xp}" y="{py - 24}" text-anchor="middle" fill="{"#86efac" if win else "#b6c4dc"}">{html.escape(label)}</text>'
            f'<text x="{xp}" y="{py + 4}" text-anchor="middle" font-size="9.5" font-weight="800" fill="#fff">{p["nodes"]}</text>'
            f'<text class="th" x="{xp}" y="{py + 32}" text-anchor="middle" fill="{"#86efac" if win else "#e2e8f0"}">'
            f'{"★ " if win else ""}worst case {val}{" (cut off)" if p["cut"] else ""}</text></g>')
        for c, cy in zip(p["children"], ys):
            worst = (not c["pruned"]) and c["name"] == p["worst"]
            if c["pruned"]:
                stroke, dash, wd = "#64748b", "5 5", 1.6
            else:
                stroke, dash, wd = ("#f59e0b", "none", 4.5) if (win and worst) else ("#ef4444", "none", 2.6) if worst else ("#2f3d5c", "none", 1.6)
            edges.append(f'<path d="M{xp},{py} C{(xp + xc) / 2},{py} {(xp + xc) / 2},{cy} {xc},{cy}" fill="none" stroke="{stroke}" '
                         f'stroke-width="{wd}" stroke-dasharray="{dash}" class="seq" data-seq="{c["seq"]}" opacity="{.55 if c["pruned"] else 1}"/>')
            if c["pruned"]:
                nodes.append(f'<g class="seq pr" data-seq="{c["seq"]}"><circle cx="{xc}" cy="{cy}" r="11" fill="#1e293b" stroke="#94a3b8" stroke-dasharray="3 3"/>'
                             f'<text x="{xc}" y="{cy + 4.5}" text-anchor="middle" font-size="13" fill="#e2e8f0">✂</text>'
                             f'<text class="th" x="{xc + 20}" y="{cy + 4}" fill="#94a3b8">{html.escape(c["name"])} — PRUNED, never evaluated</text></g>')
            else:
                skipped = (p["inc"], c["name"]) in pruned_in_other
                fill = "#f59e0b" if (win and worst) else "#ef4444" if worst else "#475569"
                tag = "terminal" if c["terminal"] else f'{c["nodes"] - 1} nodes below'
                extra = f'<text class="th" x="{xc + 20}" y="{cy + 17}" fill="#c4a3ff" font-size="9.5">✂ Alpha-Beta skips this branch</text>' if skipped else ""
                nodes.append(
                    f'<g class="seq" data-seq="{c["seq"]}"><circle cx="{xc}" cy="{cy}" r="{12 if worst else 9}" fill="{fill}" stroke="{"#c084fc" if skipped else "#e2e8f0"}" '
                    f'stroke-width="{2.5 if skipped else 1.2}" {'stroke-dasharray="3,3"' if skipped else ""}/>'
                    f'<text class="th" x="{xc + 20}" y="{cy + 4}" fill="{"#fde68a" if (win and worst) else "#e2e8f0" if worst else "#9fb0cc"}">'
                    f'{html.escape(c["name"])}  →  U = {c["value"]:.1f}  <tspan fill="#6b7fa3" font-size="9.5">({tag})</tspan></text>{extra}</g>')
        if not p["children"]:
            nodes.append(f'<g class="seq" data-seq="{p["seq"]}"><text class="th" x="{xp + 24}" y="{py + 4}" fill="#9fb0cc">no ambulance/bed → leaf U = {p["value"]:.1f}</text></g>')
    s.append("".join(edges))
    s.append(f'<g><rect x="{xr - 34}" y="{ry - 22}" width="68" height="44" rx="8" fill="#1d4ed8" stroke="#bfdbfe" stroke-width="2"/>'
             f'<text x="{xr}" y="{ry - 2}" text-anchor="middle" font-size="12" font-weight="800" fill="#fff">MAX</text>'
             f'<text x="{xr}" y="{ry + 12}" text-anchor="middle" font-size="9" fill="#bfdbfe">dispatcher</text></g>')
    s.append("".join(nodes))
    s.append(f'<text x="{xp}" y="18" text-anchor="middle" class="th" fill="#7aa2ff">MAX chooses the first dispatch</text>'
             f'<text x="{xc}" y="18" text-anchor="middle" class="th" fill="#fca5a5">MIN replies with the worst event</text>')
    s.append("</svg>")
    return "".join(s)


def tree_html(mm_tree, ab_tree):
    """Both decision trees stacked, with a replay button that reveals nodes in evaluation order."""
    saved = 1 - ab_tree["nodes"] / mm_tree["nodes"] if mm_tree["nodes"] else 0
    head = lambda t, extra: (f'<div class="th2"><b>{t["algo"]}</b><span>{t["nodes"]} nodes evaluated</span>'
                             f'<span>{t["pruned"]} cutoffs</span><span>chosen: <b style="color:#86efac">{t["action"]}</b></span>'
                             f'<span>utility {t["utility"]:.2f}</span>{extra}</div>')
    body = ('<div class="tapp"><div class="bar"><button class="go" id="t-replay">▶ Replay search order</button>'
            '<span class="note">Green = chosen plan · amber = the adversary’s worst reply · ✂ = pruned by Alpha-Beta · '
            '<b>diamond number</b> = nodes searched under that plan · U = utility (higher is better for MAX)</span></div>'
            f'<div class="tbox">{head(mm_tree, "")}<div class="scroll">{_tree_svg(mm_tree, ab_tree)}</div></div>'
            f'<div class="tbox">{head(ab_tree, f"<span style=color:#86efac>saves {saved:.0%} of the nodes</span>")}'
            f'<div class="scroll">{_tree_svg(ab_tree)}</div></div></div>')
    return _page(body, A.TREE_JS, {}, A.TREE_CSS)


# -------------------------------------------------------------------- CSP cards
def csp_cards_html(prep, alloc):
    """One card per open incident: the chosen ambulance/hospital and the constraints checked."""
    ambs = {a["id"]: a for a in prep["ambulances"]}
    hosp = {h["name"]: h for h in prep["hospitals"]}
    used_amb = {v[0]: k for k, v in alloc["assignments"].items()}
    used_beds = {}
    for v in alloc["assignments"].values():
        used_beds[v[1]] = used_beds.get(v[1], 0) + 1
    failed = {f["incident"]: f for f in alloc["failed"]}
    ok = lambda good, text: f'<div class="ck {"y" if good else "n"}"><b>{"✔" if good else "✖"}</b>{html.escape(text)}</div>'
    out = []
    for inc in sorted(prep["incidents"], key=lambda i: (-i["severity"], i["id"])):
        need, sev, iid = inc["need"], inc["severity"], inc["id"]
        head = (f'<div class="ch"><span class="sv" style="background:{SEV_COLOR[sev]}">{sev}</span><b>{iid}</b>'
                f'<span class="mu">{html.escape(inc["location"])} · {html.escape(inc["desc"])}</span><span class="need">needs {need}</span></div>')
        if iid in alloc["assignments"]:
            amb, h, total, eta = alloc["assignments"][iid]
            dom = alloc["domains"][iid]
            checks = [ok(True, f"Equipment: {amb} carries {', '.join(ambs[amb]['equipment'])} (needs {need})"),
                      ok(True, f"Availability: {amb} is available and serves only this incident"),
                      ok(True, f"Hospital: {h} offers {need}; {hosp[h]['free']} free bed(s), {used_beds[h]} planned"),
                      ok(True, f"Reachable: {eta:.1f} min to scene, {total:.1f} min including the trip to hospital")]
            rows = []
            for k, (da, dh, dt, de) in enumerate(dom[:5]):
                if (da, dh) == (amb, h):
                    state, mark = "chosen", "✔"
                elif da in used_amb and used_amb[da] != iid:
                    state, mark = f"{da} is already sent to {used_amb[da]}", "✖"
                elif used_beds.get(dh, 0) >= hosp[dh]["free"]:
                    state, mark = f"{dh} has no bed left for this plan", "✖"
                elif dt < total:
                    state, mark = "faster, but it cannot be combined with the other assignments", "✖"
                else:
                    state, mark = "slower than the chosen option", "–"
                rows.append(f'<div class="op {"on" if mark == "✔" else ""}"><b>{mark}</b> {da} → {dh} · {dt:.1f} min · {html.escape(state)}</div>')
            more = f"<div class='op'>… and {len(dom) - 5} more legal option(s)</div>" if len(dom) > 5 else ""
            note = (f'<div class="why"><b>Options considered (fastest first)</b>{"".join(rows)}{more}</div>')
            body = (f'<div class="flow"><span class="pill a">🚑 {amb}</span><span class="ar">➜</span><span class="pill i">{iid}</span>'
                    f'<span class="ar">➜</span><span class="pill h">🏥 {h}</span></div>{"".join(checks)}{note}')
            out.append(f'<div class="cc good">{head}{body}</div>')
        else:
            f = failed.get(iid, {"reason": "not assigned"})
            equipped = [a for a in prep["ambulances"] if need in a["equipment"]]
            suitable = [x for x in prep["hospitals"] if need in x["services"]]
            checks = [ok(bool(equipped), f"Equipment: {len(equipped)} available ambulance(s) carry {need}"),
                      ok(bool([x for x in suitable if x["free"] > 0]), f"Hospital: {len([x for x in suitable if x['free'] > 0])} hospital(s) offer {need} with a free bed")]
            out.append(f'<div class="cc bad">{head}<div class="flow"><span class="pill x">✖ NOT ALLOCATED</span></div>{"".join(checks)}'
                       f'<div class="why bad">{html.escape(f["reason"])}</div></div>')
    return "".join(out)


def tree_height(tree):
    """Pixel height of the component that shows two stacked trees (used by the GUI)."""
    rows = sum(max(1, len(p["children"])) for p in tree["plans"])
    return 2 * (rows * 30 + 22 * len(tree["plans"]) + 70 + 54) + 70

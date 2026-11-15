"""CSP resource allocation: each incident gets one ambulance and one hospital.

Variables : open incidents
Domain    : (ambulance, hospital) pairs that are compatible and reachable
Constraints: an ambulance serves one incident, a hospital cannot exceed its
             free beds, equipment/services must match the patient need.
Search    : backtracking + MRV variable ordering + forward checking.
"""
INF = float("inf")


def build_domains(incidents, ambulances, hospitals, amb_inc, inc_hosp):
    """For every incident list all legal (ambulance, hospital, total, eta) values,
    cheapest first."""
    domains = {}
    for inc in incidents:
        values = []
        for a in ambulances:
            if inc["need"] not in a["equipment"]:
                continue
            eta = amb_inc[(a["id"], inc["id"])]
            if eta == INF:
                continue
            for h in hospitals:
                if h["free"] <= 0 or inc["need"] not in h["services"]:
                    continue
                to_hospital = inc_hosp[(inc["id"], h["name"])]
                if to_hospital == INF:
                    continue
                values.append((a["id"], h["name"], round(eta + to_hospital, 2), round(eta, 2)))
        values.sort(key=lambda v: v[2])
        domains[inc["id"]] = values
    return domains


def choose_variable(domains, severity):
    """MRV: pick the incident with the fewest remaining options.
    Ties go to the more severe patient."""
    return min(domains, key=lambda v: (len(domains[v]), -severity[v]))


def solve(domains, severity, free_beds, trace=None):
    """Backtracking search. Returns (assignment or None, stats).
    If `trace` is a list, every real step of the search is appended to it
    (pick / try / forward / wipeout / backtrack / solution) for the GUI."""
    stats = {"calls": 0, "backtracks": 0, "fc_prunes": 0}

    def note(**event):
        if trace is not None and len(trace) < 400:
            trace.append(event)

    def backtrack(assignment, domains, beds_used):
        stats["calls"] += 1
        depth = len(assignment)
        if not domains:                       # every incident has a value
            note(kind="solution", depth=depth)
            return assignment
        var = choose_variable(domains, severity)
        note(kind="pick", depth=depth, var=var, sizes={k: len(v) for k, v in domains.items()})
        for n, value in enumerate(domains[var], 1):
            amb, hosp = value[0], value[1]
            note(kind="try", depth=depth, var=var, value=value, n=n, of=len(domains[var]))
            new_beds = dict(beds_used)
            new_beds[hosp] += 1
            # Forward checking: remove values that now clash with this choice.
            new_domains, removed = {}, {}
            wiped_out = None
            for other, values in domains.items():
                if other == var:
                    continue
                kept = [v for v in values if v[0] != amb and new_beds[v[1]] < free_beds[v[1]]]
                removed[other] = [("ambulance", v[0]) if v[0] == amb else ("hospital", v[1])
                                  for v in values if v not in kept]
                if not kept:                  # 'other' has no options left
                    wiped_out = other
                    break
                new_domains[other] = kept
            note(kind="forward", depth=depth, var=var, amb=amb, hosp=hosp, removed=removed,
                 sizes={k: len(v) for k, v in new_domains.items()}, wiped=wiped_out)
            if wiped_out:
                stats["fc_prunes"] += 1
            else:
                result = backtrack({**assignment, var: value}, new_domains, new_beds)
                if result is not None:
                    return result
            stats["backtracks"] += 1
            note(kind="backtrack", depth=depth, var=var, value=value)
        return None

    return backtrack({}, domains, {h: 0 for h in free_beds}), stats


def _arrives(eta):
    return "already at the scene" if eta == 0 else f"reaches the scene in {eta:.1f} min"


def trace_lines(trace):
    """Turn a recorded search into plain sentences: [(indent, icon, text)]."""
    out = []
    for e in trace:
        d, k = e["depth"], e["kind"]
        if k == "pick":
            sizes = ", ".join(f"{i}: {n}" for i, n in sorted(e["sizes"].items(), key=lambda kv: (kv[1], kv[0])))
            out.append((d, "🎯", f"Choose {e['var']} next (MRV = fewest legal options). Options left per incident: {sizes}."))
        elif k == "try":
            amb, hosp, total, eta = e["value"]
            out.append((d, "➡", f"Try {amb} → {e['var']} → {hosp} ({_arrives(eta)}, whole trip {total:.1f} min). "
                                f"Option {e['n']} of {e['of']}, fastest first."))
        elif k == "forward":
            parts = []
            for other, gone in e["removed"].items():
                if gone:
                    why = {}
                    for what, name in gone:
                        why[(what, name)] = why.get((what, name), 0) + 1
                    reasons = ", ".join(f"{n}× {name} {'is now used' if what == 'ambulance' else 'has no bed left'}"
                                        for (what, name), n in why.items())
                    parts.append(f"{other} loses {len(gone)} option(s) ({reasons})")
            text = "Forward checking: " + ("; ".join(parts) if parts else "no other incident loses an option") + "."
            out.append((d + 1, "🔍", text))
            if e["wiped"]:
                out.append((d + 1, "✖", f"Dead end: {e['wiped']} would have no legal option left, so this choice is rejected immediately."))
        elif k == "backtrack":
            amb, hosp = e["value"][0], e["value"][1]
            out.append((d, "↩", f"Undo {amb} → {e['var']} → {hosp} and try the next option."))
        elif k == "solution":
            out.append((d, "✔", "Every incident now has an ambulance and a hospital without breaking a constraint."))
    return out


def explain_empty(inc, ambulances, hospitals, amb_inc, inc_hosp):
    """Say why an incident has no legal (ambulance, hospital) option at all."""
    need, reasons = inc["need"], []
    equipped = [a for a in ambulances if need in a["equipment"]]
    if not equipped:
        reasons.append(f"no available ambulance carries {need} equipment")
    elif all(amb_inc[(a["id"], inc["id"])] == INF for a in equipped):
        reasons.append("equipped ambulances cannot reach the scene (roads blocked)")
    suitable = [h for h in hospitals if need in h["services"]]
    if not suitable:
        reasons.append(f"no hospital offers {need} care")
    elif not [h for h in suitable if h["free"] > 0]:
        reasons.append(f"every hospital offering {need} care is full")
    elif all(inc_hosp[(inc["id"], h["name"])] == INF for h in suitable if h["free"] > 0):
        reasons.append("suitable hospitals cannot be reached (roads blocked)")
    return "; ".join(reasons) or "no compatible ambulance/hospital pair exists"


def allocate(incidents, ambulances, hospitals, amb_inc, inc_hosp):
    """Allocate incidents in priority order (most severe first).
    Incidents that cannot be served are reported with a reason."""
    domains = build_domains(incidents, ambulances, hospitals, amb_inc, inc_hosp)
    severity = {i["id"]: i["severity"] for i in incidents}
    free_beds = {h["name"]: h["free"] for h in hospitals}
    failed = []

    # Step 1: incidents with an empty domain can never be served.
    active = []
    for inc in sorted(incidents, key=lambda i: (-i["severity"], i["id"])):
        if domains[inc["id"]]:
            active.append(inc)
        else:
            failed.append({"incident": inc["id"], "severity": inc["severity"], "need": inc["need"],
                           "reason": explain_empty(inc, ambulances, hospitals, amb_inc, inc_hosp)})

    # Step 2: add incidents one by one, most severe first. An incident is kept
    # only if the CSP is still solvable with it; otherwise it is reported as failed.
    assignment, total_stats = {}, {"calls": 0, "backtracks": 0, "fc_prunes": 0}
    accepted, rounds = [], []
    for inc in active:
        sub = {i["id"]: domains[i["id"]] for i in accepted + [inc]}
        trace = []
        result, stats = solve(sub, severity, free_beds, trace)
        rounds.append({"incident": inc["id"], "severity": inc["severity"], "accepted": result is not None,
                       "with": [i["id"] for i in accepted], "trace": trace, "stats": stats})
        for k in total_stats:
            total_stats[k] += stats[k]
        if result is not None:
            accepted.append(inc)
            assignment = result
        else:
            ambs = sorted({v[0] for v in domains[inc["id"]]})
            hosps = sorted({v[1] for v in domains[inc["id"]]})
            failed.append({"incident": inc["id"], "severity": inc["severity"], "need": inc["need"],
                           "reason": f"constraint conflict: its options (ambulances {ambs}, hospitals {hosps}) "
                                     f"are all needed by higher-priority incidents (ambulance used once, "
                                     f"hospital beds limited)."})
    return {"assignments": assignment, "failed": failed, "stats": total_stats, "domains": domains, "rounds": rounds}


def describe_plan(incidents, ambulances, alloc):
    """Plain-language view of the result.
    Returns (sentences per incident, one row per ambulance saying what it does and why)."""
    inc = {i["id"]: i for i in incidents}
    sentences = []
    for iid, (amb, hosp, total, eta) in sorted(alloc["assignments"].items(), key=lambda kv: (-inc[kv[0]]["severity"], kv[0])):
        i = inc[iid]
        sentences.append(f"**{iid}** (severity {i['severity']}, needs {i['need']}, at {i['location']}): send **{amb}** ({_arrives(eta)}), "
                         f"then it takes the patient to **{hosp}** "
                         f"({total - eta:.1f} more min).")
    by_amb = {v[0]: (k, v) for k, v in alloc["assignments"].items()}
    failed = {f["incident"] for f in alloc["failed"]}
    rows = []
    for a in ambulances:
        if a["status"] == "Disabled":
            role = "Out of service - not used."
        elif a["status"] == "Busy":
            role = "Already on a mission - not used."
        elif a["id"] in by_amb:
            iid, (_, hosp, total, eta) = by_amb[a["id"]]
            role = f"Goes to {iid} at {inc[iid]['location']} ({'already there' if eta == 0 else f'{eta:.1f} min away'}), then to {hosp}."
        else:
            can = [i["id"] for i in incidents if i["need"] in a["equipment"]]
            if not can:
                role = f"Spare: no open emergency needs its equipment ({', '.join(a['equipment'])})."
            else:
                parts = []
                for iid in can:
                    who = alloc["assignments"][iid][0] if iid in alloc["assignments"] else None
                    parts.append(f"{iid} (covered by {who})" if who else f"{iid} ({'could not be served' if iid in failed else 'not assigned'})")
                role = "Spare: it could serve " + ", ".join(parts) + "."
        rows.append({"Ambulance": a["id"], "Base": a["base"], "Carries": ", ".join(a["equipment"]), "What it does": role})
    return sentences, rows

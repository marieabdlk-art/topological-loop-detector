from __future__ import annotations
import numpy as np
import pandas as pd

def predict_loop_probability(model, row, cols):
    X = pd.DataFrame([row[cols]]).replace([np.inf, -np.inf], np.nan).fillna(0)
    return float(model.predict_proba(X)[0, 1])

def trigger_policy_for_trajectory(g, model, cols, policy="vnext1_gated", tau_trig=0.08, p_alert=0.75, min_watch_windows=3):
    state = "SILENT"
    first_alert = None
    watch_count = 0
    g = g.sort_values("window_end").reset_index(drop=True)
    for _, row in g.iterrows():
        candidate = (row["topo_max"] > tau_trig) or (row["topo_top2_sum"] > 2*tau_trig)
        if policy == "generic":
            rejected = False; classifier_ok = True; min_ok = True
        elif policy == "vnext1_gated":
            rejected = bool(row.get("reject_transient", 0) or row.get("reject_shrinking", 0))
            classifier_ok = predict_loop_probability(model, row, cols) >= p_alert
            min_ok = watch_count >= min_watch_windows
        else:
            raise ValueError(policy)
        if state == "SILENT":
            if candidate and not rejected:
                state = "WATCH"; watch_count = 1
        elif state == "WATCH":
            watch_count += 1
            confirmed = ((row["current_h1_streak"] >= 2 and row["topo_max"] > tau_trig) or (row["current_multibar_streak"] >= 2 and row["topo_top2_sum"] > 2*tau_trig))
            if rejected:
                state = "SILENT"; watch_count = 0
            elif confirmed and min_ok and classifier_ok:
                first_alert = int(row["window_end"]); break
    return int(first_alert is not None), first_alert

def simulate_trigger_policies(feat_df, trajs, test_ids, model, cols, policies=("generic", "vnext1_gated")):
    rows=[]
    for tid,g in feat_df.groupby("traj_id"):
        if tid not in test_ids:
            continue
        obj=trajs[tid]
        row={"traj_id":tid,"regime":obj.regime,"difficulty":obj.difficulty,"label_loop":obj.label_loop}
        for policy in policies:
            alerted, first_alert = trigger_policy_for_trajectory(g, model, cols, policy=policy)
            row[f"{policy}_alerted"] = alerted
            row[f"{policy}_first_alert"] = first_alert
            row[f"{policy}_correct"] = int(alerted == obj.label_loop)
        rows.append(row)
    return pd.DataFrame(rows)

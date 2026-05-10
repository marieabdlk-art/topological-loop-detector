from __future__ import annotations
import pandas as pd

def model_accuracy_table(results):
    return pd.DataFrame({
        "model": list(results.keys()),
        "test_accuracy": [r["accuracy"] for r in results.values()],
    }).sort_values("test_accuracy", ascending=False).reset_index(drop=True)

def trigger_summary(trigger_df):
    agg = {"label_loop": ("label_loop", "first"), "n": ("traj_id", "size")}
    for col in trigger_df.columns:
        if col.endswith("_alerted"):
            agg[col.replace("_alerted", "_alert_rate")] = (col, "mean")
        if col.endswith("_first_alert"):
            agg[col.replace("_first_alert", "_mean_first_alert")] = (col, "mean")
        if col.endswith("_correct"):
            agg[col.replace("_correct", "_accuracy")] = (col, "mean")
    return trigger_df.groupby("regime").agg(**agg).reset_index()

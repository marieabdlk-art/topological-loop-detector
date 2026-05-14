from __future__ import annotations

import argparse
import pandas as pd

from topoloop.benchmark import run_single_benchmark


def parse_args():
    parser = argparse.ArgumentParser(description="Run multi-seed Topological Loop Detector benchmark.")
    parser.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2, 3, 4])
    parser.add_argument("--n-per-regime", type=int, default=30)
    parser.add_argument("--split-mode", choices=["trajectory", "hard_generalization", "both"], default="both")
    return parser.parse_args()


def mean_std(df: pd.DataFrame, group_cols: list[str], value_cols: list[str]) -> pd.DataFrame:
    rows = []
    for keys, g in df.groupby(group_cols):
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = dict(zip(group_cols, keys))
        for col in value_cols:
            row[f"{col}_mean"] = g[col].mean()
            row[f"{col}_std"] = g[col].std()
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    args = parse_args()
    split_modes = ["trajectory", "hard_generalization"] if args.split_mode == "both" else [args.split_mode]

    summaries = []
    per_regime_tables = []
    trigger_tables = []

    for split_mode in split_modes:
        for seed in args.seeds:
            print(f"running seed={seed}, split_mode={split_mode}")
            out = run_single_benchmark(seed=seed, n_per_regime=args.n_per_regime, split_mode=split_mode)
            summaries.append(out["summary"])
            pr = out["per_regime"].copy()
            pr["seed"] = seed
            pr["split_mode"] = split_mode
            per_regime_tables.append(pr)
            tr = out["trigger_df"].copy()
            tr["seed"] = seed
            tr["split_mode"] = split_mode
            trigger_tables.append(tr)

    summary_df = pd.concat(summaries, ignore_index=True)
    per_regime_df = pd.concat(per_regime_tables, ignore_index=True)
    trigger_df = pd.concat(trigger_tables, ignore_index=True)

    summary_stats = mean_std(
        summary_df,
        ["split_mode"],
        [
            "topo_max_accuracy",
            "geometry_accuracy",
            "temporal_accuracy",
            "combined_accuracy",
            "generic_trigger_accuracy",
            "vnext1_trigger_accuracy",
        ],
    )

    fpr_stats = (
        per_regime_df[per_regime_df["FPR_if_nonloop"].notna()]
        .groupby(["split_mode", "model", "regime"])
        .agg(FPR_mean=("FPR_if_nonloop", "mean"), FPR_std=("FPR_if_nonloop", "std"))
        .reset_index()
    )

    tpr_stats = (
        per_regime_df[per_regime_df["TPR_if_loop"].notna()]
        .groupby(["split_mode", "model", "regime"])
        .agg(TPR_mean=("TPR_if_loop", "mean"), TPR_std=("TPR_if_loop", "std"))
        .reset_index()
    )

    trigger_stats = (
        trigger_df.groupby(["split_mode", "regime"])
        .agg(
            label_loop=("label_loop", "first"),
            generic_alert_rate=("generic_alerted", "mean"),
            vnext1_alert_rate=("vnext1_gated_alerted", "mean"),
            generic_accuracy=("generic_correct", "mean"),
            vnext1_accuracy=("vnext1_gated_correct", "mean"),
            n=("traj_id", "size"),
        )
        .reset_index()
    )

    print("\n=== MULTI-SEED SUMMARY ===")
    print(summary_stats.round(4).to_string(index=False))

    print("\n=== NEAR-MISS FPR ===")
    print(fpr_stats[fpr_stats["regime"] == "near_miss_spiral"].round(4).to_string(index=False))

    print("\n=== LOOP TPR ===")
    print(tpr_stats.round(4).to_string(index=False))

    summary_df.to_csv("multiseed_summary_raw.csv", index=False)
    summary_stats.to_csv("multiseed_summary_stats.csv", index=False)
    per_regime_df.to_csv("multiseed_per_regime.csv", index=False)
    fpr_stats.to_csv("multiseed_fpr_stats.csv", index=False)
    tpr_stats.to_csv("multiseed_tpr_stats.csv", index=False)
    trigger_stats.to_csv("multiseed_trigger_stats.csv", index=False)


if __name__ == "__main__":
    main()

from __future__ import annotations
from sklearn.model_selection import train_test_split
from topoloop.generators import make_dataset
from topoloop.features import BASELINE_COLS, H1_PROFILE_COLS, topk_cols, build_window_table, add_temporal_features, add_rejection_flags_vnext1
from topoloop.models import fit_binary_models, per_regime_table
from topoloop.trigger import simulate_trigger_policies
from topoloop.evaluation import model_accuracy_table, trigger_summary

SEED = 42
K = 8
TEMPORAL_COLS = [
    "mean_topo_max_last_m", "std_topo_max_last_m",
    "mean_topo_top2_sum_last_m", "std_topo_top2_sum_last_m",
    "mean_topo_top3_sum_last_m", "std_topo_top3_sum_last_m",
    "mean_top2_over_top1_last_m", "std_top2_over_top1_last_m",
    "mean_bar_entropy_last_m", "std_bar_entropy_last_m",
    "mean_n_bars_tau_last_m", "std_n_bars_tau_last_m",
    "mean_closure_norm_last_m", "std_closure_norm_last_m",
    "mean_radius_slope_last_m", "std_radius_slope_last_m",
    "mean_centroid_drift_norm_last_m", "std_centroid_drift_norm_last_m",
    "mean_nearest_return_norm_last_m", "std_nearest_return_norm_last_m",
    "fraction_h1_active", "fraction_count_tau_ge_2",
    "current_h1_streak", "current_multibar_streak",
    "profile_total_variation", "post_peak_decay_rate", "h1_survival_after_peak",
]
REJECTION_COLS = ["reject_transient", "reject_shrinking"]

def main():
    trajs = make_dataset(n_per_regime=30, seed=SEED)
    feat = build_window_table(trajs, window_size=64, stride=4, k_bars=K)
    feat = add_temporal_features(feat)
    feat = add_rejection_flags_vnext1(feat)

    meta = feat[["traj_id", "regime", "difficulty"]].drop_duplicates()
    strat = meta["regime"] + "::" + meta["difficulty"]
    train_ids, test_ids = train_test_split(meta["traj_id"].values, test_size=0.30, random_state=SEED, stratify=strat)

    train_df = feat[feat["traj_id"].isin(train_ids)].copy()
    test_df = feat[feat["traj_id"].isin(test_ids)].copy()

    feature_sets = {
        "topo_max_only": ["topo_max"],
        "temporal_h1_profile": H1_PROFILE_COLS + topk_cols(K) + TEMPORAL_COLS,
        "combined_hybrid": BASELINE_COLS + H1_PROFILE_COLS + topk_cols(K) + TEMPORAL_COLS + REJECTION_COLS,
    }

    results = fit_binary_models(train_df, test_df, feature_sets, seed=SEED)
    predictions = {name: r["pred"] for name, r in results.items()}
    per_regime = per_regime_table(test_df, predictions)

    combined_model = results["combined_hybrid"]["model"]
    combined_cols = feature_sets["combined_hybrid"]
    trigger_df = simulate_trigger_policies(feat, trajs, set(test_ids), combined_model, combined_cols)

    print("\n=== MAIN MODEL ACCURACY ===")
    print(model_accuracy_table(results).to_string(index=False))
    print("\n=== PER-REGIME ACCURACY ===")
    print(per_regime.pivot(index="regime", columns="model", values="accuracy").round(3).to_string())
    print("\n=== HARD NEGATIVE FPR ===")
    print(per_regime[per_regime["FPR_if_nonloop"].notna()].pivot(index="regime", columns="model", values="FPR_if_nonloop").round(3).to_string())
    print("\n=== TRIGGER SUMMARY ===")
    print(trigger_summary(trigger_df).round(3).to_string(index=False))

    feat.to_csv("window_features.csv", index=False)
    model_accuracy_table(results).to_csv("model_accuracy.csv", index=False)
    per_regime.to_csv("per_regime.csv", index=False)
    trigger_df.to_csv("trigger_trajectory.csv", index=False)
    trigger_summary(trigger_df).to_csv("trigger_summary.csv", index=False)

if __name__ == "__main__":
    main()

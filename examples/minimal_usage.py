"""Minimal usage example for the current repository implementation.

Run from the repository root:

    python examples/minimal_usage.py

This example intentionally uses the implemented compact architecture:
H1-profile features + temporal features + combined hybrid classifier.
"""

from sklearn.model_selection import train_test_split

from topoloop.generators import make_dataset
from topoloop.features import (
    BASELINE_COLS,
    H1_PROFILE_COLS,
    add_rejection_flags_vnext1,
    add_temporal_features,
    build_window_table,
    topk_cols,
)
from topoloop.models import fit_binary_models, per_regime_table


SEED = 42
K_BARS = 8

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


def main() -> None:
    # 1. Generate a small synthetic dataset.
    trajs = make_dataset(n_per_regime=3, seed=SEED)

    # 2. Convert trajectories to sliding-window features.
    features = build_window_table(trajs, window_size=64, stride=8, k_bars=K_BARS)
    features = add_temporal_features(features)
    features = add_rejection_flags_vnext1(features)

    # 3. Split by trajectory id, not by window, to avoid leakage.
    meta = features[["traj_id", "regime", "difficulty"]].drop_duplicates()
    train_ids, test_ids = train_test_split(
        meta["traj_id"].values,
        test_size=0.30,
        random_state=SEED,
        stratify=meta["regime"] + "::" + meta["difficulty"],
    )

    train_df = features[features["traj_id"].isin(train_ids)]
    test_df = features[features["traj_id"].isin(test_ids)]

    # 4. Train the implemented compact feature sets.
    feature_sets = {
        "topo_max_only": ["topo_max"],
        "combined_hybrid": BASELINE_COLS
        + H1_PROFILE_COLS
        + topk_cols(K_BARS)
        + TEMPORAL_COLS
        + REJECTION_COLS,
    }

    results = fit_binary_models(train_df, test_df, feature_sets, seed=SEED)
    predictions = {name: result["pred"] for name, result in results.items()}

    print("Model accuracies:")
    for name, result in results.items():
        print(f"  {name}: {result['accuracy']:.3f}")

    print("\nPer-regime accuracy:")
    table = per_regime_table(test_df, predictions)
    print(table.pivot(index="regime", columns="model", values="accuracy").round(3))


if __name__ == "__main__":
    main()

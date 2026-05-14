from __future__ import annotations

import math
import pandas as pd
from sklearn.model_selection import train_test_split

from .generators import make_dataset
from .features import (
    BASELINE_COLS,
    H1_PROFILE_COLS,
    add_rejection_flags_vnext1,
    add_temporal_features,
    build_window_table,
    topk_cols,
)
from .models import fit_binary_models, per_regime_table
from .trigger import simulate_trigger_policies


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


def feature_sets(k_bars: int = 8) -> dict[str, list[str]]:
    return {
        "topo_max_only": ["topo_max"],
        "geometry_only": BASELINE_COLS,
        "temporal_h1_profile": H1_PROFILE_COLS + topk_cols(k_bars) + TEMPORAL_COLS,
        "combined_hybrid": BASELINE_COLS + H1_PROFILE_COLS + topk_cols(k_bars) + TEMPORAL_COLS + REJECTION_COLS,
    }


def _valid_stratification(candidate: pd.Series, n_samples: int, test_size: float = 0.30) -> bool:
    counts = candidate.value_counts()
    if counts.min() < 2:
        return False

    n_classes = len(counts)
    n_test = math.ceil(n_samples * test_size)
    n_train = n_samples - n_test
    return n_test >= n_classes and n_train >= n_classes


def _safe_stratification(meta: pd.DataFrame, test_size: float = 0.30) -> pd.Series | None:
    """Choose the most specific valid stratification available.

    Full benchmark runs can stratify by regime+difficulty. Tiny CI smoke tests
    may be too small for stratified splitting. In that case we fall back to a
    coarser stratification, and finally to an unstratified split.
    """
    n_samples = len(meta)

    by_regime_and_difficulty = meta["regime"] + "::" + meta["difficulty"]
    if _valid_stratification(by_regime_and_difficulty, n_samples, test_size):
        return by_regime_and_difficulty

    by_regime = meta["regime"]
    if _valid_stratification(by_regime, n_samples, test_size):
        return by_regime

    return None


def split_trajectory_ids(feat: pd.DataFrame, seed: int, split_mode: str = "trajectory"):
    meta = feat[["traj_id", "regime", "difficulty"]].drop_duplicates()

    if split_mode == "hard_generalization":
        train_ids = meta[meta["difficulty"].isin(["easy", "medium"] )]["traj_id"].values
        test_ids = meta[meta["difficulty"].isin(["hard"] )]["traj_id"].values
        return train_ids, test_ids

    if split_mode != "trajectory":
        raise ValueError(f"Unknown split_mode: {split_mode}")

    test_size = 0.30
    strat = _safe_stratification(meta, test_size=test_size)
    return train_test_split(
        meta["traj_id"].values,
        test_size=test_size,
        random_state=seed,
        stratify=strat,
    )


def run_single_benchmark(
    seed: int = 42,
    n_per_regime: int = 30,
    window_size: int = 64,
    stride: int = 4,
    k_bars: int = 8,
    split_mode: str = "trajectory",
):
    trajs = make_dataset(n_per_regime=n_per_regime, seed=seed)
    feat = build_window_table(trajs, window_size=window_size, stride=stride, k_bars=k_bars)
    feat = add_temporal_features(feat)
    feat = add_rejection_flags_vnext1(feat)

    train_ids, test_ids = split_trajectory_ids(feat, seed=seed, split_mode=split_mode)
    train_df = feat[feat["traj_id"].isin(train_ids)].copy()
    test_df = feat[feat["traj_id"].isin(test_ids)].copy()

    sets = feature_sets(k_bars)
    results = fit_binary_models(train_df, test_df, sets, seed=seed)
    predictions = {name: r["pred"] for name, r in results.items()}
    per_regime = per_regime_table(test_df, predictions)

    combined_model = results["combined_hybrid"]["model"]
    combined_cols = sets["combined_hybrid"]
    trigger_df = simulate_trigger_policies(feat, trajs, set(test_ids), combined_model, combined_cols)

    summary = {
        "seed": seed,
        "split_mode": split_mode,
        "n_per_regime": n_per_regime,
        "topo_max_accuracy": results["topo_max_only"]["accuracy"],
        "geometry_accuracy": results["geometry_only"]["accuracy"],
        "temporal_accuracy": results["temporal_h1_profile"]["accuracy"],
        "combined_accuracy": results["combined_hybrid"]["accuracy"],
        "generic_trigger_accuracy": trigger_df["generic_correct"].mean(),
        "vnext1_trigger_accuracy": trigger_df["vnext1_gated_correct"].mean(),
    }

    return {
        "summary": pd.DataFrame([summary]),
        "feature_table": feat,
        "per_regime": per_regime,
        "trigger_df": trigger_df,
        "results": results,
    }

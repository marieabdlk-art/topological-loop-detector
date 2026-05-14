from __future__ import annotations

import argparse

from .benchmark import run_single_benchmark
from .evaluation import model_accuracy_table, trigger_summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Topological Loop Detector benchmark.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--n-per-regime", type=int, default=30)
    parser.add_argument("--split-mode", choices=["trajectory", "hard_generalization"], default="trajectory")
    parser.add_argument("--window-size", type=int, default=64)
    parser.add_argument("--stride", type=int, default=4)
    args = parser.parse_args()

    out = run_single_benchmark(
        seed=args.seed,
        n_per_regime=args.n_per_regime,
        window_size=args.window_size,
        stride=args.stride,
        split_mode=args.split_mode,
    )

    results = out["results"]
    per_regime = out["per_regime"]
    trigger_df = out["trigger_df"]

    print("\n=== MAIN MODEL ACCURACY ===")
    print(model_accuracy_table(results).to_string(index=False))

    print("\n=== PER-REGIME ACCURACY ===")
    print(per_regime.pivot(index="regime", columns="model", values="accuracy").round(3).to_string())

    print("\n=== HARD NEGATIVE FPR ===")
    print(
        per_regime[per_regime["FPR_if_nonloop"].notna()]
        .pivot(index="regime", columns="model", values="FPR_if_nonloop")
        .round(3)
        .to_string()
    )

    print("\n=== TRIGGER SUMMARY ===")
    print(trigger_summary(trigger_df).round(3).to_string(index=False))


if __name__ == "__main__":
    main()

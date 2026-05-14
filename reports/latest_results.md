# Latest Results

This report records the current repository-generated benchmark results.

## Status

- GitHub Actions workflow: **green**.
- Scope: **detection only**.
- Escape / recovery / rescue logic: **out of scope** for this repository.

---

## Reproducibility status

CI smoke test runs:

```bash
pytest -q
python experiments/run_vnext1.py
python experiments/run_multiseed.py --seeds 0 1 --n-per-regime 5 --split-mode trajectory
```

Full benchmark command used for this report:

```bash
python experiments/run_multiseed.py --seeds 0 1 2 3 4 --n-per-regime 30 --split-mode both
```

This report is based on generated CSV files:

```text
multiseed_summary_raw.csv
multiseed_summary_stats.csv
multiseed_per_regime.csv
multiseed_fpr_stats.csv
multiseed_tpr_stats.csv
multiseed_trigger_stats.csv
```

---

## Main multiseed summary

Mean ± std across 5 seeds.

| Split mode | topo_max acc | geometry acc | temporal H1 acc | combined acc | generic trigger acc | vNext1 trigger acc |
|---|---:|---:|---:|---:|---:|---:|
| `trajectory` | 0.5871 ± 0.0024 | 0.8292 ± 0.0115 | 0.9121 ± 0.0062 | **0.9333 ± 0.0065** | 0.5096 ± 0.0103 | **0.9481 ± 0.0101** |
| `hard_generalization` | 0.4264 ± 0.0031 | 0.5833 ± 0.0132 | 0.6469 ± 0.0095 | **0.6645 ± 0.0088** | 0.4313 ± 0.0061 | **0.7280 ± 0.0168** |

Interpretation:

```text
combined_hybrid > temporal_h1_profile > geometry_only > topo_max_only
```

This supports the narrow repository claim that richer H1-profile + temporal features are stronger than scalar `topo_max`.

---

## Trajectory split: loop-family TPR

| Regime | topo_max | geometry | temporal H1 | combined hybrid |
|---|---:|---:|---:|---:|
| `clean_loop` | 0.667 | 0.764 | 0.855 | **0.900** |
| `drifting_loop` | 0.667 | 0.769 | **0.941** | 0.940 |
| `figure_eight` | 0.000 | 0.918 | 0.937 | **0.951** |
| `multi_loop_bridge` | 0.096 | 0.857 | 0.928 | **0.969** |

Key result:

```text
topo_max fails on figure_eight and multi_loop_bridge;
H1-profile / combined features recover these families.
```

---

## Trajectory split: hard-negative FPR

| Regime | topo_max | geometry | temporal H1 | combined hybrid |
|---|---:|---:|---:|---:|
| `convergence` | 0.000 | 0.000 | 0.001 | **0.000** |
| `near_miss_spiral` | 0.667 | 0.754 | 0.418 | **0.327** |
| `noisy_pseudoloop` | 0.000 | 0.191 | 0.078 | **0.073** |
| `self_intersect_convergence` | 0.000 | 0.008 | 0.020 | **0.003** |
| `shrinking_loop_to_goal` | 0.891 | 0.000 | 0.003 | **0.000** |
| `transient_loop` | 0.000 | 0.063 | 0.020 | 0.024 |

Main remaining hard negative:

```text
near_miss_spiral
```

Even the best model still has FPR ≈ 0.327 on trajectory split and ≈ 0.375 on hard-generalization split.

---

## Online trigger summary

| Split | Policy | Accuracy |
|---|---|---:|
| `trajectory` | generic | 0.5096 ± 0.0103 |
| `trajectory` | vNext1 gated | **0.9481 ± 0.0101** |
| `hard_generalization` | generic | 0.4313 ± 0.0061 |
| `hard_generalization` | vNext1 gated | **0.7280 ± 0.0168** |

The gated trigger greatly reduces over-alerting, especially on hard negatives.

---

## Trigger alert rates by regime

### Trajectory split

| Regime | label | generic alert | vNext1 alert |
|---|---:|---:|---:|
| `clean_loop` | 1 | 1.000 | 0.911 |
| `drifting_loop` | 1 | 1.000 | 0.993 |
| `figure_eight` | 1 | 1.000 | 0.978 |
| `multi_loop_bridge` | 1 | 1.000 | 1.000 |
| `convergence` | 0 | 1.000 | 0.000 |
| `near_miss_spiral` | 0 | 1.000 | 0.311 |
| `noisy_pseudoloop` | 0 | 0.815 | 0.037 |
| `self_intersect_convergence` | 0 | 0.563 | 0.000 |
| `shrinking_loop_to_goal` | 0 | 1.000 | 0.000 |
| `transient_loop` | 0 | 0.526 | 0.052 |

### Hard-generalization split

| Regime | label | generic alert | vNext1 alert |
|---|---:|---:|---:|
| `clean_loop` | 1 | 1.000 | 0.120 |
| `drifting_loop` | 1 | 1.000 | 0.473 |
| `figure_eight` | 1 | 1.000 | 0.760 |
| `multi_loop_bridge` | 1 | 1.000 | 0.447 |
| `convergence` | 0 | 0.987 | 0.000 |
| `near_miss_spiral` | 0 | 1.000 | 0.493 |
| `noisy_pseudoloop` | 0 | 0.800 | 0.027 |
| `self_intersect_convergence` | 0 | 0.900 | 0.000 |
| `shrinking_loop_to_goal` | 0 | 1.000 | 0.000 |
| `transient_loop` | 0 | 1.000 | 0.000 |

Important limitation:

```text
hard_generalization exposes under-alerting on true loop families,
especially clean_loop and multi_loop_bridge.
```

This means the detector is much stronger under trajectory-level random split than under difficulty-shift split.

---

## Negative result retained from vNext2/vNext3

Earlier experiments tested hard / conditional near-miss rejection. That line was not retained because it suppressed true complex loops such as:

```text
figure_eight
multi_loop_bridge
```

Current conclusion:

```text
near-miss evidence should be a classifier feature,
not an unconditional pre-alert hard rejection rule.
```

---

## Current defensible claim

> H1-profile temporal topology provides a stronger loop-detection signal than scalar `topo_max`, especially for complex loop families, and classifier-gated triggering is safer than generic threshold triggering under trajectory-level random split.

The hard-generalization split is substantially weaker and should be treated as the main next research target.

Not claimed:

```text
production-ready loop guard
escape / recovery system
full v6/v7 implementation
universal real-agent detector
```

---

## Next engineering targets

1. Improve hard-generalization recall for true loop families.
2. Reduce `near_miss_spiral` FPR without suppressing figure-eight / multi-loop.
3. Add family-aware calibration instead of one global threshold.
4. Add real LLM-agent traces.
5. Add stronger non-topological recurrence baselines.

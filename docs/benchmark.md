# Benchmark

This benchmark is a synthetic controlled testbed for topological loop detection.

It is designed to answer a narrow question:

> Does H1-profile temporal topology provide a useful signal for detecting persistent loop-like trajectory structure, especially beyond scalar `topo_max`?

---

## Benchmark regimes

### Positive regimes

| Regime | Description | Why it matters |
|---|---|---|
| `clean_loop` | Stable circular trajectory | Basic sanity check |
| `drifting_loop` | Loop with moving center | Breaks exact-repeat logic |
| `figure_eight` | Two-lobed self-intersecting loop | Requires multi-bar/family-aware features |
| `multi_loop_bridge` | Two loops connected by bridge | Tests multi-loop structure |

### Hard negatives

| Regime | Description | Failure mode tested |
|---|---|---|
| `convergence` | Monotone convergence to goal | Should not alert |
| `transient_loop` | Loop-like event that decays | Static topology can false-positive |
| `noisy_pseudoloop` | Noise-induced pseudo-hole | Tests robustness to accidental H1 |
| `near_miss_spiral` | Almost closes but does not | Main hard negative |
| `shrinking_loop_to_goal` | Spiral-like convergence | Should not be treated as trap-loop |
| `self_intersect_convergence` | Self-crossing convergence | Tests that crossing ≠ loop |

---

## Feature families

### 1. Scalar topological baseline

```text
topo_max_only = [topo_max]
```

This is intentionally weak. It tests whether one scalar persistence value is enough.

### 2. H1-profile temporal model

Uses richer H1-profile and temporal features:

```text
H1_PROFILE_COLS + top-K bars + TEMPORAL_COLS
```

### 3. Combined hybrid model

Adds baseline geometry and rejection flags:

```text
BASELINE_COLS + H1_PROFILE_COLS + top-K bars + TEMPORAL_COLS + REJECTION_COLS
```

---

## Evaluation outputs

The benchmark prints and writes:

```text
MAIN MODEL ACCURACY
PER-REGIME ACCURACY
HARD NEGATIVE FPR
TRIGGER SUMMARY
```

Generated files:

```text
window_features.csv
model_accuracy.csv
per_regime.csv
trigger_trajectory.csv
trigger_summary.csv
```

---

## How to run

```bash
pip install -r requirements.txt
python experiments/run_vnext1.py
```

Or through GitHub Actions:

```text
Actions → benchmark → Run workflow
```

---

## Correct interpretation

A good result is not just high overall accuracy.

The important checks are:

1. `combined_hybrid` should outperform `topo_max_only`.
2. Complex positive families should not collapse:
   - `figure_eight`
   - `multi_loop_bridge`
3. Hard negative FPR should be monitored separately:
   - `near_miss_spiral`
   - `noisy_pseudoloop`
   - `transient_loop`
4. `vnext1_gated` should improve over `generic` online triggering.

---

## Why hard near-miss rejection is not included

Experiments with vNext2/vNext3 showed that spiral-aware hard rejection can reduce some false positives, but it also suppresses true complex loops.

Observed pattern:

```text
vNext1 gated trigger: best balance
vNext2/vNext3 hard/conditional spiral rejection: lower recall on figure-eight and multi-loop
```

Therefore near-miss evidence should be handled by the classifier, not by unconditional hard rejection.

---

## Limitations

This benchmark is synthetic. It does not prove production-readiness on real LLM-agent traces.

Main limitations:

```text
2D synthetic state space
simple classifiers
no real agent logs yet
no representative cycle extraction
no v6/v7 full architecture yet
```

The correct next step is not to claim universality, but to extend the benchmark to:

```text
higher-dimensional embeddings
real agent traces
stronger recurrence baselines
separate online trigger stress tests
```

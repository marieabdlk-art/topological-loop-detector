# Experimental Results

This document separates two things:

1. **What is implemented in this repository now**
2. **Historical Colab experiments that motivated the current architecture**

The current repository implements a compact, reproducible benchmark around:

```text
H1-profile + temporal features + combined hybrid classifier + classifier-gated trigger
```

It does **not** claim to implement the full v6/v7 research architecture yet.

---

## Current repository benchmark

Run:

```bash
python experiments/run_vnext1.py
```

The script generates synthetic 2D trajectories, builds sliding-window H1 profiles, trains simple classifiers, and compares:

```text
topo_max_only
temporal_h1_profile
combined_hybrid
```

It also compares two online trigger policies:

```text
generic
vnext1_gated
```

The script writes:

```text
window_features.csv
model_accuracy.csv
per_regime.csv
trigger_trajectory.csv
trigger_summary.csv
```

These files are ignored by git and should be treated as local benchmark artifacts.

---

## Historical vNext Colab result used to choose current repo direction

The strongest compact version from the vNext experiments was the classifier-gated trigger rather than hard near-miss rejection.

One later vNext run reported:

| Metric | Value |
|---|---:|
| `topo_max_accuracy` | 0.585333 |
| `temporal_accuracy` | 0.9512 |
| `combined_accuracy` | 0.968622 |
| `family_accuracy` | 0.984444 |
| `generic_trigger_acc` | 0.537778 |
| `vnext1_trigger_acc` | 0.973333 |
| `vnext2_trigger_acc` | 0.920000 |
| `vnext3_trigger_acc` | 0.920000 |

Interpretation:

```text
vNext1 gated trigger > vNext2 / vNext3 hard or conditional spiral rejection
```

The important negative result:

```text
hard near-miss / spiral rejection suppresses true complex loops such as figure-eight and multi-loop bridge
```

So near-miss features should be used by the classifier, not as an unconditional pre-alert blocker.

---

## Earlier architecture trajectory

### MVP / v2

Early experiments showed that H1 persistence can detect drifting cycles where near-repeat baselines fail. The key conceptual shift was:

```text
cycle ≠ exact state repetition
cycle = persistent loop-like structure in trajectory geometry
```

### v3

v3 showed that static topology is strong, but temporal validation is needed to reject transient or pseudo-loop artifacts.

Important lesson:

```text
static topology proposes loop candidates;
temporal topology validates whether the loop persists.
```

The main weakness in v3 was that temporal features were too focused on a single dominant H1 bar, hurting figure-eight and multi-loop regimes.

### v4

v4 added diagram-stability and family-aware temporal features. This fixed the earlier multi-loop weakness but exposed noisy pseudoloop discrimination as the main remaining failure mode.

Reported result pattern:

```text
temporal_v3_only = 0.800
temporal_v4_only = 0.963
```

### v5

v5 added more object-aware temporal signals such as centroid drift, bar inertia, and weighted persistence. This improved noisy pseudoloop handling while preserving performance on transient and shrinking-loop regimes.

### v6

v6 moved from pure classification toward family-aware online triggering.

Reported online trigger result:

| Trigger policy | Trajectory-level accuracy |
|---|---:|
| generic | 0.683 |
| v6 family-aware | 0.817 |

Important remaining weaknesses:

```text
multi_loop trajectory aggregation
transient_loop suppression in online trigger
```

---

## What this repository currently claims

Defensible current claim:

> H1-profile temporal topology gives a stronger structural signal than scalar `topo_max`, especially for complex loop families, and classifier-gated triggering is safer than generic threshold triggering.

Not claimed:

```text
This is not a universal production-ready agent loop detector.
This repository does not yet implement the full v6/v7 architecture.
This repository does not include Orthogonal Escape.
```

---

## Main remaining limitation

The hardest negative class remains:

```text
near-miss / almost-loop trajectories
```

The correct direction is not a hard reject rule, but better family-aware classifier features and temporal validation.

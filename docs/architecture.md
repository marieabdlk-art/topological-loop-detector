# Architecture

This repository implements a compact experimental architecture for topological loop detection in synthetic agent trajectories.

The implemented pipeline is intentionally narrower than the full research roadmap.

---

## Implemented pipeline

```text
Synthetic trajectory
        ↓
Sliding windows
        ↓
Vietoris–Rips complex
        ↓
H1 persistence diagram
        ↓
H1-profile encoder
        ↓
Temporal features
        ↓
Binary classifier
        ↓
Classifier-gated trigger
```

---

## 1. Synthetic trajectory stream

Trajectories are generated in `src/topoloop/generators.py`.

Positive loop regimes:

```text
clean_loop
drifting_loop
figure_eight
multi_loop_bridge
```

Hard negative regimes:

```text
convergence
transient_loop
noisy_pseudoloop
near_miss_spiral
shrinking_loop_to_goal
self_intersect_convergence
```

The goal is not to claim real-agent generality yet. The benchmark is a controlled environment for testing whether topology carries useful signal beyond scalar recurrence or naive thresholds.

---

## 2. Sliding windows

The detector does not classify whole trajectories directly. It builds fixed-size windows:

```python
build_window_table(trajs, window_size=64, stride=4)
```

Each window is treated as a point cloud.

---

## 3. H1 persistence

For each window, the code builds a Vietoris–Rips complex and extracts finite H1 bars:

```python
h1_diagram(window)
```

The important conceptual shift is:

```text
loop = persistent shape in trajectory geometry
not necessarily exact state recurrence
```

---

## 4. H1-profile encoder

The repository does not rely only on `topo_max`.

`topo_max` is useful, but it loses structure. For example, figure-eight and multi-loop trajectories may not be represented by one dominant bar.

The profile includes:

```text
topo_max
topo_sum
n_bars_tau
topo_top2_sum
topo_top3_sum
top2_over_top1
top3_over_top1
bar_entropy
bar_concentration
persistence_gini
birth_mean / birth_std
death_mean / death_std
top-K birth/death/persistence bars
```

This is implemented in:

```text
src/topoloop/topology.py
```

---

## 5. Temporal features

Static topology can falsely activate on transient or noisy pseudo-loops.

Temporal features ask whether H1 structure persists across nearby windows:

```text
mean_topo_max_last_m
std_topo_max_last_m
fraction_h1_active
current_h1_streak
current_multibar_streak
profile_total_variation
post_peak_decay_rate
h1_survival_after_peak
```

These features are implemented in:

```text
src/topoloop/features.py
```

Design principle:

```text
static topology proposes candidates;
temporal topology validates persistence.
```

---

## 6. Classifiers

The current implementation uses simple logistic regression with standard scaling.

This is intentional: the goal is to test whether the features carry signal, not to hide performance inside a complex model.

Implemented model families:

```text
topo_max_only
temporal_h1_profile
combined_hybrid
```

---

## 7. Online trigger policy

The trigger layer compares:

```text
generic
vnext1_gated
```

`generic` mostly uses direct H1 thresholding.

`vnext1_gated` requires:

1. candidate topological evidence,
2. temporal consistency,
3. classifier probability above threshold,
4. rejection flags for obvious transient/shrinking cases.

The key negative result from the experiments is that hard near-miss rejection should not be used as a universal pre-alert blocker because it can suppress true complex loop families.

---

## What is not implemented here yet

This repository currently does **not** implement:

```text
full v6 family-aware trigger
v7 unified topological guard
orthogonal escape control
representative cycle extraction
witness complex acceleration
semantic LLM gate
```

Those are research-roadmap items, not current repository claims.

---

## Current architectural claim

The current repository supports this narrow claim:

> H1-profile plus temporal validation gives a stronger loop signal than scalar `topo_max`, and classifier-gated online triggering is safer than generic threshold triggering.

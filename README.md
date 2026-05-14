# Topological Loop Detector

Topological Loop Detector detects cyclic failure modes in agent/model trajectories by treating loops as **structural closure of a trajectory**, not just repeated states.

Current best architecture:

```text
H1-profile temporal detector + hybrid classifier + classifier-gated online trigger
```

## Scope

This repository focuses on **detection only**.

Out of scope for this repository:

```text
escape / recovery / rescue policies
context surgery
orthogonal escape
agent intervention logic
```

The detector output can be used by downstream recovery systems later, but this repository intentionally keeps recovery separate.

## Core idea

Most loop detectors rely on exact repeats, cosine similarity, token repetition, timeout, or max-step limits. This project uses H1 persistent homology on sliding windows to detect when a trajectory forms a loop-like structure.

## Why H1-profile

A scalar metric like `topo_max` is not enough. It fails on structurally non-trivial regimes such as `figure_eight` and `multi_loop_bridge`.

The detector uses a richer H1 profile:

- `topo_max`
- `topo_sum`
- `n_bars_tau`
- `topo_top2_sum`
- `topo_top3_sum`
- `top2_over_top1`
- `bar_entropy`
- top-K birth/death/persistence bars
- temporal stability features
- geometry features

## Benchmark regimes

Positive loops:

```text
clean_loop
drifting_loop
figure_eight
multi_loop_bridge
```

Hard negatives:

```text
convergence
transient_loop
noisy_pseudoloop
near_miss_spiral
shrinking_loop_to_goal
self_intersect_convergence
```

## Model comparisons

The benchmark now compares:

```text
topo_max_only
geometry_only
temporal_h1_profile
combined_hybrid
```

Main expected result pattern:

```text
topo_max_only < temporal_h1_profile < combined_hybrid
```

The `geometry_only` baseline is included to separate topology-specific signal from non-topological geometric cues.

Online trigger result pattern:

```text
generic trigger < classifier-gated trigger
```

Important negative result:

```text
hard spiral / near-miss rejection hurts figure-eight and multi-loop recall
```

So near-miss features should be used by the classifier, not as unconditional hard pre-alert rejection.

## Quick start

```bash
pip install -r requirements.txt
python experiments/run_vnext1.py
```

CLI:

```bash
topoloop-benchmark --seed 42 --n-per-regime 30
```

Multi-seed benchmark:

```bash
python experiments/run_multiseed.py --seeds 0 1 2 3 4 --n-per-regime 30
```

## Structure

```text
src/topoloop/           detector package
experiments/            benchmark runners
tests/                  unit and smoke tests
docs/                   architecture and benchmark docs
.github/workflows/      GitHub Actions benchmark
reports/                report templates
```

## Status

Experimental research package. Not a universal solved loop detector.

Main current limitation: near-miss / almost-loop trajectories remain the hardest false-positive class.

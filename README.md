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

## Current results

See the full report:

```text
reports/latest_results.md
```

Repository-generated multiseed benchmark:

```bash
python experiments/run_multiseed.py --seeds 0 1 2 3 4 --n-per-regime 30 --split-mode both
```

Mean ± std across 5 seeds:

| Split mode | topo_max acc | geometry acc | temporal H1 acc | combined acc | generic trigger acc | vNext1 trigger acc |
|---|---:|---:|---:|---:|---:|---:|
| `trajectory` | 0.5871 ± 0.0024 | 0.8292 ± 0.0115 | 0.9121 ± 0.0062 | **0.9333 ± 0.0065** | 0.5096 ± 0.0103 | **0.9481 ± 0.0101** |
| `hard_generalization` | 0.4264 ± 0.0031 | 0.5833 ± 0.0132 | 0.6469 ± 0.0095 | **0.6645 ± 0.0088** | 0.4313 ± 0.0061 | **0.7280 ± 0.0168** |

Key interpretation:

```text
combined_hybrid > temporal_h1_profile > geometry_only > topo_max_only
```

The hard-generalization split is substantially weaker than the trajectory split and is the main next research target.

## Real LLM pilot: TinyLlama v10 Master

Beyond the synthetic benchmark, the project also has a real-model pilot on a TinyLlama generation trace.

In that experiment, direct H1 persistence on raw embeddings was blind because the representation cloud collapsed during repeated generation. A lagged embedding reconstruction:

```text
(V_t, V_{t-lag})
```

made the hidden loop topologically visible. Around generation step ~30, the H1 signal rose to approximately `0.018`, and temporal bridging stabilized the detector output.

See:

```text
docs/real_llm_pilot_v10_master.md
```

This is the strongest reason the project can move toward a production observability tool: the method is not only a synthetic 2D benchmark idea, but a representation-dependent detector that has already shown signal on a real LLM trace.

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

Main remaining hard negative:

```text
near_miss_spiral
```

Even the current best model has FPR around 0.327 on trajectory split and 0.375 on hard-generalization split.

## Model comparisons

The benchmark compares:

```text
topo_max_only
geometry_only
temporal_h1_profile
combined_hybrid
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
python experiments/run_multiseed.py --seeds 0 1 2 3 4 --n-per-regime 30 --split-mode both
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

Main current limitations:

```text
near_miss / almost-loop false positives
weak hard-generalization recall on true loop families
real LLM pilot exists, but real-trace benchmark is not implemented yet
```

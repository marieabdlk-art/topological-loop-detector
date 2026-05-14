# Latest Results

This report records the latest validated results available for the repository.

## Status

- GitHub Actions workflow: **green** after the stratified split fix.
- Scope: **detection only**.
- Escape / recovery / rescue logic: **out of scope** for this repository.

---

## Reproducibility status

The repository now contains a working CI workflow that runs:

```bash
pytest -q
python experiments/run_vnext1.py
python experiments/run_multiseed.py --seeds 0 1 --n-per-regime 5 --split-mode trajectory
```

The CI run verifies that:

```text
package installation works
tests pass
single benchmark runs
multi-seed smoke benchmark runs
```

---

## Recorded vNext.3 Colab result

The following result comes from the latest recorded vNext.3 Colab experiment in the research log. It is not yet the same as the current repository benchmark because the repository has since added a separate `geometry_only` baseline.

| Metric | Value |
|---|---:|
| `topo_max_accuracy` | 0.585333 |
| `temporal_accuracy` | 0.951200 |
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

---

## Trigger alert rates from the same recorded run

| Regime | Label loop | Generic alert | vNext1 alert | vNext2 alert | vNext3 alert |
|---|---:|---:|---:|---:|---:|
| `clean_loop` | 1 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| `convergence` | 0 | 0.977778 | 0.000000 | 0.000000 | 0.000000 |
| `drifting_loop` | 1 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| `figure_eight` | 1 | 1.000000 | 1.000000 | 0.600000 | 0.600000 |
| `multi_loop_bridge` | 1 | 1.000000 | 1.000000 | 0.822222 | 0.844444 |
| `near_miss_spiral` | 0 | 1.000000 | 0.200000 | 0.200000 | 0.200000 |
| `noisy_pseudoloop` | 0 | 0.688889 | 0.044444 | 0.000000 | 0.022222 |
| `self_intersect_convergence` | 0 | 0.488889 | 0.000000 | 0.000000 | 0.000000 |
| `shrinking_loop_to_goal` | 0 | 1.000000 | 0.000000 | 0.000000 | 0.000000 |
| `transient_loop` | 0 | 0.466667 | 0.022222 | 0.022222 | 0.022222 |

Main result:

```text
vNext1 preserves figure-eight and multi-loop recall better than vNext2/vNext3.
```

---

## Negative result

The vNext2/vNext3 line tested hard or conditional near-miss / spiral rejection.

Result:

```text
hard near-miss rejection suppresses true complex loops
```

Affected true-loop families:

```text
figure_eight
multi_loop_bridge
```

Conclusion:

```text
near-miss evidence should be a classifier feature, not an unconditional pre-alert hard rejection rule
```

---

## Current repository benchmark status

The repository now includes an additional baseline:

```text
geometry_only
```

Therefore the exact current repository benchmark should be regenerated with:

```bash
python experiments/run_multiseed.py --seeds 0 1 2 3 4 --n-per-regime 30 --split-mode both
```

This full run is intentionally heavier than the CI smoke benchmark.

The next publication-ready results table should include:

```text
topo_max_only
geometry_only
temporal_h1_profile
combined_hybrid
```

and should report:

```text
mean ± std across seeds
trajectory split
hard_generalization split
hard-negative FPR
loop-family TPR
trigger accuracy
```

---

## Current defensible claim

> H1-profile temporal topology provides a stronger loop-detection signal than scalar `topo_max`, especially for complex loop families, and classifier-gated triggering is safer than generic threshold triggering.

Not claimed:

```text
production-ready loop guard
escape / recovery system
full v6/v7 implementation
universal real-agent detector
```

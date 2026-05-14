# TAG v7 / v7.1: Unified Topological Guard

This document records the future architecture direction for TAG v7. It is **not** the current implementation in this repository.

Current repository scope:

```text
detection only
```

TAG v7 scope:

```text
closed-loop detection + early warning + control / intervention
```

Therefore TAG v7 is tracked here as a roadmap architecture, not as a current repository claim.

---

## 1. Executive summary

The current detector line works as:

```text
Detect → Alert
```

Earlier v6-style designs also considered:

```text
Detect → Escape
```

TAG v7 proposes a stronger unified architecture:

```text
continuous topological monitoring → early warning → closed-loop control
```

Core idea:

> Persistent topology should not only emit a binary `LOOP_DETECTED` signal after a loop is complete. It should provide a continuous warning/control signal while the loop is forming.

---

## 2. Main v7 components

| Layer | Purpose |
|---|---|
| H1-profile / persistence landscape | Continuous structural loop intensity |
| Early warning signals | Detect pre-persistence loop formation |
| Dimensionality reduction | Make high-dimensional traces tractable |
| Temporal tracking | Stabilize features across windows |
| Semantic gate | Distinguish harmful loop from useful refinement spiral |
| Control interface | Translate loop signal into agent intervention |

---

## 3. Detection-only vs Unified Guard

| Component | Current repository | TAG v7 roadmap |
|---|---|---|
| Synthetic benchmark | implemented | reused |
| H1 profile | implemented | reused |
| Temporal features | implemented | extended |
| Classifier-gated trigger | implemented | replaced by continuous warning/control |
| Real LLM lagged trace | documented pilot | should be implemented |
| Escape / recovery | out of scope | in scope |
| Closed-loop control | not implemented | proposed |
| Semantic gate | not implemented | proposed |

Important:

```text
Do not describe TAG v7 as implemented until its modules exist in code.
```

---

## 4. Early warning: corrected v7.1 design

The original v7 idea proposed a Hodge-Laplacian spectral warning signal. The corrected v7.1 design replaces the fragile spectral claim with a persistence-landscape warning.

### Incorrect earlier claim

The earlier draft suggested a strong monotonic lead-time theorem based on the smallest nonzero Hodge eigenvalue.

Problem:

```text
lambda* is not guaranteed to decrease monotonically when edges/simplices are added.
```

### Corrected signal: landscape early warning

Use the level-1 persistence landscape:

```text
Lambda_1(t, epsilon)
```

Define sub-threshold area:

```text
A_sub(t) = integral min(Lambda_1(t, epsilon), pi_0) d epsilon
```

Then use its positive growth:

```text
S_landscape(t) = sigmoid( positive_delta(A_sub(t)) / A_ref )
```

This is safer because sub-threshold landscape mass can appear before a bar crosses the full detection threshold.

Correct claim:

> Sub-threshold persistence landscape activity can precede a thresholded H1-bar alarm, provided a nascent H1 feature exists below the alarm threshold.

Not claimed:

```text
universal fixed lead-time bound in steps
```

---

## 5. Other early warning signals

### 5.1 Return proximity

Tracks whether the current state approaches a previous segment of the trajectory:

```text
r(t) = min ||x_t - x_j|| over old j in the window
```

Useful for cheap online risk detection.

### 5.2 Adaptive winding

The original v7 used PC1-PC2 winding. v7.1 corrects this using local adaptive PCA and a planarity check.

Principle:

```text
compute winding only when the local trajectory tail is sufficiently planar
```

This avoids false confidence when the cycle is not actually represented in the first two global principal components.

### 5.3 Signal fusion

The original noisy-OR fusion was overconfident under correlated signals.

Corrected options:

```text
weighted max
or calibrated logistic regression
```

Default conservative fusion:

```text
W(t) = max(w_i * S_i)
```

---

## 6. Scaling to high-dimensional traces

TAG v7 proposes:

```text
raw embedding d → Sparse Random Projection → epochal PCA → H1 computation
```

Corrected design:

1. Fixed Sparse Random Projection.
2. Epochal PCA, not per-step arbitrary PCA.
3. Procrustes alignment between PCA epochs.
4. Optional witness complex / landmark approximation.

Why epochal PCA:

```text
If the PCA basis changes every step, bar matching across windows can become unstable.
```

Corrected strategy:

```text
freeze PCA basis within an epoch
realign basis via Procrustes between epochs
```

---

## 7. Witness complex caveat

Witness complexes can miss H1 features that Vietoris-Rips would capture.

Therefore v7.1 treats witness complex as an acceleration path, not as a guaranteed replacement.

Required validation:

```text
compare VR diagram vs witness diagram
measure bottleneck distance
increase landmarks if fidelity is insufficient
```

---

## 8. Escape/control direction correction

The earlier v7 draft proposed lifting a direction from projected space using:

```text
v_orig = S.T @ v_projected
```

This is not a true pseudoinverse and can distort the escape direction.

Corrected design:

```text
use projected space only for detection
compute escape direction in original space using raw window vectors
```

Algorithm:

1. Detect representative cycle in projected space.
2. Map representative vertex indices back to raw vectors in `window_raw`.
3. Compute PCA of those raw cycle vertices.
4. Project current velocity onto the orthogonal complement of that raw cycle subspace.

Principle:

```text
project for detection, act in original space
```

---

## 9. Control stability correction

The original PD-control proposal had no plant model for the agent.

Corrected v7.1 uses safeguard logic:

```text
if persistence energy worsens after intervention:
    shrink gains
if it improves consistently:
    slowly restore gains
always clamp ||u|| <= u_max
```

This makes the controller fail-safe: if the intervention is harmful, gains decay toward zero.

---

## 10. Semantic gate

TAG v7 distinguishes:

| Pattern | Geometry | Decision |
|---|---|---|
| refinement spiral | loop-like orthogonal motion + task progress | allow |
| hallucination loop | H1 loop + no progress | intervene |
| regressive loop | H1 loop + negative progress | intervene urgently |

The semantic gate requires a task/progress axis:

```text
e_task
```

Possible definitions:

1. goal embedding minus initial embedding;
2. learned quality-gradient direction;
3. PCA direction from successful traces;
4. external task metric.

This is not yet implemented.

---

## 11. LLM control interface

For LLM agents, `u(t)` cannot simply be added to a physical action vector.

Possible interfaces:

| Agent type | Control variable |
|---|---|
| sampler | temperature / top-p / repetition penalty |
| tool agent | tool choice / prompt routing / planning reset |
| soft-prompt model | soft prompt embedding perturbation |
| observability-only mode | alert + evidence report, no intervention |

For this repository, the near-term production path should be:

```text
observability-only mode first
```

not direct intervention.

---

## 12. Stress tests for v7

### Test 1: early warning lead

Goal:

```text
landscape early warning should activate before thresholded H1 alarm
```

Metrics:

```text
landscape lead time
false positive rate before loop
warning stability
```

### Test 2: high-dimensional sparse cycle

Goal:

```text
SRP + epochal PCA should preserve loop signal in high-dimensional traces
```

Metrics:

```text
VR vs projected bottleneck distance
throughput
effective dimension
```

### Test 3: semantic spiral vs harmful loop

Goal:

```text
semantic gate should allow refinement spirals but flag no-progress loops
```

Metrics:

```text
classification accuracy
false suppression rate
latency to harmful-loop flag
```

---

## 13. Relationship to TinyLlama v10 Master

TinyLlama v10 Master showed that raw embeddings can be topologically blind and that lagged reconstruction can restore loop visibility.

TAG v7 should incorporate this lesson:

```text
observation representation is part of the detector
```

Future v7 real-trace module should support:

```text
raw hidden states
lagged hidden states
embedding deltas
temporal bridge
landscape early warning
```

---

## 14. Implementation priority

Do **not** implement full closed-loop escape first.

Recommended order:

1. `real_trace.py`: lagged embedding reconstruction + temporal bridge.
2. `early_warning.py`: landscape / return / adaptive winding signals.
3. `projection.py`: SRP + epochal PCA.
4. `stress_tests_v7.py`: high-dimensional synthetic tests.
5. `semantic_gate.py`: classification only, no intervention.
6. Control/intervention layer only after observability evidence is strong.

---

## 15. Current repo claim remains unchanged

TAG v7 is a roadmap architecture.

Current implemented claim:

> H1-profile temporal topology outperforms scalar topo_max and geometry-only baselines on synthetic trajectory splits, and classifier-gated triggering reduces over-alerting.

Future TAG v7 claim, after implementation:

> A unified topology-enhanced guard can detect, anticipate, classify, and eventually steer loop-prone agent trajectories using continuous persistence-derived warning signals.

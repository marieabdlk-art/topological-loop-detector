# Real LLM Pilot: TinyLlama v10 Master

This document records the real-model pilot experiment that motivated the production direction of the project.

The synthetic benchmark is not the whole story. The strongest qualitative result so far is that the detector was also tested on a real generation trace from a small language model.

---

## Summary

Experiment:

```text
Topological loop detection on TinyLlama generation trace
```

Key result:

> Hidden loop behavior in TinyLlama became topologically visible through lagged embedding reconstruction, even when direct H1 persistence on raw embeddings was blind.

This is important because it shows that the method is not limited to synthetic 2D trajectories. It can expose a loop-like structure in an actual LLM hidden-state trajectory, provided the representation is chosen correctly.

---

## 1. Problem: raw embedding topology can be blind

In the repeated generation regime:

```text
—\n—\n—\n...
```

TinyLlama hidden states in the inspected layers became nearly indistinguishable in representation space.

Observed behavior:

```text
raw embedding H1 persistence ≈ 0
```

Interpretation:

The point cloud collapsed. The behavioral loop existed at the generation level, but direct topological analysis of raw embeddings did not produce a stable one-dimensional hole.

Consequence:

```text
behavioral loop exists
but naive raw-embedding H1 is blind
```

This is a critical production lesson: the detector cannot depend only on raw embedding topology.

---

## 2. Solution: lagged embedding reconstruction

Instead of analyzing a single hidden state vector:

```text
V_t
```

v10 Master used a lagged phase-space representation:

```text
(V_t, V_{t-lag})
```

The purpose is to recover local dynamics when individual states collapse or become too similar.

Intuition:

```text
If states are almost identical, analyze state transitions / delayed coordinates, not just states.
```

After lagged reconstruction, the repeated generation regime formed a loop-like structure in reconstructed phase space, making an H1 signal computable with GUDHI.

---

## 3. Technical parameters

Recorded v10 Master configuration:

| Parameter | Value |
|---|---|
| Model | TinyLlama |
| Generation regime | repeated `—\n` pattern |
| Layer | layer 20 |
| Representation | lagged embedding reconstruction |
| Analysis window | last 25 tokens |
| Max edge length | 2.0 for normalized vectors |
| Temporal bridge | 15 steps |
| Startup suppression | ignore early transient noise |
| Signal cleanup | smoothing + ghost-hump filtering |

---

## 4. Observed v10 Master result

Observed effects:

1. Direct H1 on raw embeddings did not produce a useful signal.
2. Lagged embedding reconstruction restored topological visibility.
3. Around generation step ~30, H1 jumped to approximately `0.018`.
4. Temporal bridging maintained `Loop: True` despite short raw-signal drops.
5. Detector output became operationally stable rather than flickering.

Operational interpretation:

```text
raw H1 = blind
lagged H1 = detectable structural loop signal
temporal bridge = stable trigger state
```

---

## 5. What this proves

Within this experiment, the result supports these claims:

- the method is not restricted to synthetic 2D trajectories;
- a real TinyLlama generation trace produced a detectable loop signal;
- raw embedding topology can miss loop behavior;
- lagged embedding reconstruction can recover a hidden H1 signature;
- temporal bridging stabilizes detection at trigger level.

---

## 6. What this does not prove

This experiment does **not** yet prove:

- universal robustness across all LLMs;
- robustness across prompts, seeds, and decoding settings;
- robustness across different loop types;
- absence of false positives on benign repetition;
- semantic distinction between harmful loop and acceptable stylistic repetition.

---

## 7. Production implication

For a production detector, the key architectural update is:

```text
raw embeddings are not enough
```

Production detector should support multiple observation modes:

```text
raw hidden states
lagged hidden states
embedding deltas
tool-call traces
semantic progress features
temporal bridge state
```

The production framing should be:

```text
topology-enhanced loop detection for real agent/model traces
```

not:

```text
pure H1 on raw embeddings
```

---

## 8. Current repository status

The current repository benchmark is still synthetic and 2D. It does not yet implement the full TinyLlama v10 Master pipeline.

This document records the real-LLM pilot result and defines the next engineering target:

```text
add a real_trace/ module with lagged embedding reconstruction and temporal bridging
```

---

## Next implementation target

Recommended next module:

```text
src/topoloop/real_trace.py
```

Minimum API:

```python
from topoloop.real_trace import LaggedTraceDetector

detector = LaggedTraceDetector(layer=20, lag=2, window=25, bridge=15)
result = detector.analyze_hidden_states(hidden_states)
```

Expected outputs:

```json
{
  "loop_detected": true,
  "onset_step": 30,
  "max_h1": 0.018,
  "representation": "lagged_embedding",
  "raw_h1_blind": true,
  "bridge_active_steps": 15
}
```

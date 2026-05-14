# Failure Modes

This repository focuses on loop detection only. It does not implement escape or recovery policies.

## Main remaining hard negative

The strongest remaining hard negative is:

```text
near_miss_spiral
```

A near-miss spiral can generate loop-like H1 signal because the trajectory almost closes, but it is not a stable recurrent trap.

## Why hard near-miss rejection was not kept

Earlier experiments tested hard and conditional spiral-aware rejection. The result was negative: these rules suppressed true complex loops, especially:

```text
figure_eight
multi_loop_bridge
```

Conclusion:

```text
near-miss evidence should be a classifier feature, not an unconditional pre-alert hard reject
```

## Other failure classes

### Transient loop

A transient loop is a temporary cyclic excursion that decays quickly. Static topology can fire on it. Temporal features such as `post_peak_decay_rate` and `h1_survival_after_peak` help reject it.

### Shrinking loop to goal

This can look loop-like, but it represents convergence rather than a loop failure. The compact implementation uses radius slope and post-peak decay as rejection evidence.

### Noisy pseudoloop

Noise can create short-lived holes in the Vietoris-Rips complex. Temporal stability is required to avoid over-alerting.

## Correct design principle

```text
static topology proposes candidates;
temporal stability validates candidates;
classifier-gated triggering decides whether to alert.
```

Do not add escape/recovery logic to this repository unless it is clearly separated as a downstream module.

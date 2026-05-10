# Current Results Template

## Main accuracy

| Model | Accuracy |
|---|---:|
| topo_max_only | TBD |
| temporal_h1_profile | TBD |
| combined_hybrid | TBD |

## Trigger accuracy

| Policy | Trajectory-level accuracy |
|---|---:|
| generic | TBD |
| classifier-gated vNext1 | TBD |

## Important findings

1. `topo_max_only` is insufficient for figure-eight and multi-loop regimes.
2. H1-profile improves structural family detection.
3. Temporal features improve transient and shrinking-loop rejection.
4. Classifier-gated trigger outperforms rule-only triggering.
5. Hard spiral / near-miss rejection should not be used as a global pre-alert blocker.

## Main remaining limitation

Near-miss / almost-loop trajectories remain the strongest hard-negative class.

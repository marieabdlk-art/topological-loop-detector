from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd

LOOP_REGIMES = {"clean_loop", "drifting_loop", "figure_eight", "multi_loop_bridge"}
HARD_NEGATIVES = {"convergence", "transient_loop", "noisy_pseudoloop", "near_miss_spiral", "shrinking_loop_to_goal", "self_intersect_convergence"}

@dataclass(frozen=True)
class Trajectory:
    traj_id: int
    regime: str
    difficulty: str
    xy: np.ndarray
    label_loop: int

def _sigma(diff: str) -> float:
    return {"easy": 0.02, "medium": 0.06, "hard": 0.12}[diff]

def _noise(xy, sigma, rng):
    return xy + rng.normal(0, sigma, size=xy.shape)

def gen_clean_loop(rng, t=160, diff="medium"):
    R = rng.uniform(1, 2)
    turns = {"easy": 3, "medium": 2.5, "hard": 2}[diff]
    th = np.linspace(0, 2*np.pi*turns, t)
    return _noise(np.c_[R*np.cos(th), R*np.sin(th)], _sigma(diff), rng)

def gen_drifting_loop(rng, t=160, diff="medium"):
    R = rng.uniform(1, 2)
    turns = {"easy": 3, "medium": 2.5, "hard": 2}[diff]
    drift = {"easy": .25, "medium": .55, "hard": .85}[diff]
    th = np.linspace(0, 2*np.pi*turns, t)
    direction = rng.normal(size=2)
    direction /= np.linalg.norm(direction) + 1e-12
    base = np.c_[R*np.cos(th), R*np.sin(th)]
    return _noise(base + drift*np.linspace(0, 1, t)[:, None]*direction[None, :], _sigma(diff), rng)

def gen_figure_eight(rng, t=160, diff="medium"):
    R = rng.uniform(1, 2)
    turns = {"easy": 2, "medium": 2, "hard": 1.6}[diff]
    th = np.linspace(0, 2*np.pi*turns, t)
    xy = np.c_[R*np.sin(th), R*np.sin(th)*np.cos(th)]
    if diff == "hard":
        xy[:, 0] += .25*np.linspace(0, 1, t)
    return _noise(xy, _sigma(diff), rng)

def gen_multi_loop_bridge(rng, t=160, diff="medium"):
    t1 = t//3; t2 = t//3; t3 = t - t1 - t2
    r1 = rng.uniform(.8, 1.2); r2 = rng.uniform(.7, 1.1)
    c1 = np.array([-1.5, 0.0]); c2 = np.array([1.5, 0.0])
    th1 = np.linspace(0, 2*np.pi, t1); th2 = np.linspace(0, 2*np.pi, t3)
    loop1 = c1 + np.c_[r1*np.cos(th1), r1*np.sin(th1)]
    bridge = np.linspace(loop1[-1], c2 + np.array([r2, 0.0]), t2)
    loop2 = c2 + np.c_[r2*np.cos(th2), r2*np.sin(th2)]
    xy = np.vstack([loop1, bridge, loop2])[:t]
    if diff == "hard":
        xy[:, 1] += .2*np.sin(np.linspace(0, 7*np.pi, len(xy)))
    return _noise(xy, _sigma(diff), rng)

def gen_convergence(rng, t=160, diff="medium"):
    x = rng.uniform(-2, 2, size=2)
    goal = rng.uniform(-.2, .2, size=2)
    alpha = {"easy": .90, "medium": .94, "hard": .97}[diff]
    pts = []
    for _ in range(t):
        pts.append(x.copy()); x = goal + alpha*(x-goal)
    return _noise(np.array(pts), _sigma(diff), rng)

def gen_transient_loop(rng, t=160, diff="medium"):
    R = rng.uniform(1.2, 2)
    turns = {"easy": 1, "medium": 1.5, "hard": 2}[diff]
    decay = {"easy": 4.5, "medium": 3, "hard": 2}[diff]
    th = np.linspace(0, 2*np.pi*turns, t)
    env = np.exp(-decay*np.linspace(0, 1, t))
    return _noise(np.c_[R*env*np.cos(th), R*env*np.sin(th)], _sigma(diff), rng)

def gen_noisy_pseudoloop(rng, t=160, diff="medium"):
    sig = {"easy": .18, "medium": .28, "hard": .40}[diff]
    xy = np.cumsum(rng.normal(0, sig, size=(t, 2)), axis=0)
    th = np.linspace(0, {"easy":1.2*np.pi,"medium":1.7*np.pi,"hard":2.1*np.pi}[diff], t)
    return .55*xy + np.c_[.6*np.cos(th), .6*np.sin(th)]

def gen_near_miss_spiral(rng, t=160, diff="medium"):
    R = rng.uniform(1, 2)
    turns = {"easy": 2, "medium": 2.5, "hard": 3}[diff]
    gap = {"easy": .55, "medium": .35, "hard": .18}[diff]
    th = np.linspace(0, 2*np.pi*turns, t)
    r = R + gap*np.linspace(0, 1, t)
    return _noise(np.c_[r*np.cos(th), r*np.sin(th)], _sigma(diff), rng)

def gen_shrinking_loop_to_goal(rng, t=160, diff="medium"):
    R = rng.uniform(1.4, 2.2)
    turns = {"easy": 3, "medium": 3.5, "hard": 4}[diff]
    decay = {"easy": 1.5, "medium": 1.1, "hard": .8}[diff]
    th = np.linspace(0, 2*np.pi*turns, t)
    r = R*np.exp(-decay*np.linspace(0, 1, t))
    return _noise(np.c_[r*np.cos(th), r*np.sin(th)], _sigma(diff), rng)

def gen_self_intersect_convergence(rng, t=160, diff="medium"):
    u = np.linspace(0, 1, t); amp = 1-u
    return _noise(np.c_[amp*np.cos(4*np.pi*u), amp*np.sin(2*np.pi*u)], _sigma(diff), rng)

GENERATORS = {
    "clean_loop": gen_clean_loop,
    "drifting_loop": gen_drifting_loop,
    "figure_eight": gen_figure_eight,
    "multi_loop_bridge": gen_multi_loop_bridge,
    "convergence": gen_convergence,
    "transient_loop": gen_transient_loop,
    "noisy_pseudoloop": gen_noisy_pseudoloop,
    "near_miss_spiral": gen_near_miss_spiral,
    "shrinking_loop_to_goal": gen_shrinking_loop_to_goal,
    "self_intersect_convergence": gen_self_intersect_convergence,
}

def make_dataset(n_per_regime=50, t=160, difficulties=("easy", "medium", "hard"), seed=42):
    rng = np.random.default_rng(seed)
    out = {}; tid = 0
    for regime, fn in GENERATORS.items():
        for diff in difficulties:
            for _ in range(n_per_regime):
                xy = fn(rng, t=t, diff=diff)
                out[tid] = Trajectory(tid, regime, diff, xy, int(regime in LOOP_REGIMES))
                tid += 1
    return out

def trajectories_to_dataframe(trajs):
    rows=[]
    for tid,tr in trajs.items():
        for i,(x,y) in enumerate(tr.xy):
            rows.append({"traj_id":tid,"regime":tr.regime,"difficulty":tr.difficulty,"t":i,"x":float(x),"y":float(y),"label_loop":tr.label_loop})
    return pd.DataFrame(rows)

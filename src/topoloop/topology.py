from __future__ import annotations
import numpy as np
from scipy.spatial.distance import pdist
import gudhi as gd

def robust_window_scale(window):
    d = pdist(window)
    return float(max(np.quantile(d, 0.90), 1e-8)) if len(d) else 1.0

def max_edge_length_from_window(window, quantile=0.95):
    d = pdist(window)
    return float(max(np.quantile(d, quantile), 1e-8)) if len(d) else 1.0

def h1_diagram(window, max_edge_quantile=0.95):
    rips = gd.RipsComplex(points=window.tolist(), max_edge_length=max_edge_length_from_window(window, max_edge_quantile))
    st = rips.create_simplex_tree(max_dimension=2)
    st.persistence()
    diag = []
    for dim, bd in st.persistence():
        if dim == 1 and not np.isinf(bd[1]):
            diag.append((float(bd[0]), float(bd[1])))
    return diag

def gini(x):
    x = np.asarray(x, dtype=float)
    x = x[x > 0]
    if len(x) == 0:
        return 0.0
    x = np.sort(x)
    n = len(x)
    return float((2*np.arange(1, n+1).dot(x)/(n*x.sum())) - (n+1)/n)

def encode_h1_profile(diag, window, k=8, tau_bar=0.035):
    scale = robust_window_scale(window)
    bars = []
    for birth, death in diag:
        b = birth / scale
        d = death / scale
        p = max(0.0, d-b)
        if p > 1e-12:
            bars.append((b, d, p))
    bars = sorted(bars, key=lambda z: z[2], reverse=True)
    p_topk = np.zeros(k); b_topk = np.zeros(k); d_topk = np.zeros(k)
    for i, (b, d, p) in enumerate(bars[:k]):
        b_topk[i] = b; d_topk[i] = d; p_topk[i] = p
    pers = np.array([p for _, _, p in bars], dtype=float)
    births = np.array([b for b, _, p in bars if p > tau_bar], dtype=float)
    deaths = np.array([d for _, d, p in bars if p > tau_bar], dtype=float)
    topo_max = float(pers[0]) if len(pers) else 0.0
    topo_sum = float(pers.sum()) if len(pers) else 0.0
    n_bars_tau = int(np.sum(pers > tau_bar))
    top2_sum = float(pers[:2].sum()) if len(pers) else 0.0
    top3_sum = float(pers[:3].sum()) if len(pers) else 0.0
    top2_over_top1 = float(pers[1]/pers[0]) if len(pers) >= 2 and pers[0] > 1e-12 else 0.0
    top3_over_top1 = float(pers[2]/pers[0]) if len(pers) >= 3 and pers[0] > 1e-12 else 0.0
    if topo_sum > 1e-12:
        probs = pers / topo_sum
        bar_entropy = float(-(probs*np.log(probs+1e-12)).sum())
        bar_concentration = float(topo_max/topo_sum)
    else:
        bar_entropy = 0.0
        bar_concentration = 0.0
    out = {}
    for i in range(k):
        out[f"p_top{i+1}"] = float(p_topk[i])
        out[f"b_top{i+1}"] = float(b_topk[i])
        out[f"d_top{i+1}"] = float(d_topk[i])
    out.update({
        "scale_q90": scale,
        "n_bars_tau": n_bars_tau,
        "topo_max": topo_max,
        "topo_sum": topo_sum,
        "topo_top2_sum": top2_sum,
        "topo_top3_sum": top3_sum,
        "top2_over_top1": top2_over_top1,
        "top3_over_top1": top3_over_top1,
        "bar_entropy": bar_entropy,
        "bar_concentration": bar_concentration,
        "persistence_gini": gini(pers),
        "birth_mean": float(births.mean()) if len(births) else 0.0,
        "birth_std": float(births.std()) if len(births) else 0.0,
        "death_mean": float(deaths.mean()) if len(deaths) else 0.0,
        "death_std": float(deaths.std()) if len(deaths) else 0.0,
    })
    return out

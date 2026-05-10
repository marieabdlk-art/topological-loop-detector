from __future__ import annotations
import numpy as np
import pandas as pd
from .topology import h1_diagram, encode_h1_profile

H1_PROFILE_COLS=["topo_max","topo_sum","n_bars_tau","topo_top2_sum","topo_top3_sum","top2_over_top1","top3_over_top1","bar_entropy","bar_concentration","persistence_gini","birth_mean","birth_std","death_mean","death_std"]
BASELINE_COLS=["path_length","closure_gap","closure_norm","path_radius","radius_std","radius_cv","radius_slope","centroid_drift","centroid_drift_norm","nearest_return_dist","nearest_return_norm","turning_total"]

def topk_cols(k=8):
    return [f"p_top{i+1}" for i in range(k)] + [f"b_top{i+1}" for i in range(k)] + [f"d_top{i+1}" for i in range(k)]

def baseline_geometry(window):
    diffs=np.diff(window,axis=0)
    path_length=float(np.linalg.norm(diffs,axis=1).sum()) if len(diffs) else 0.0
    closure_gap=float(np.linalg.norm(window[-1]-window[0]))
    center=window.mean(axis=0)
    radius=np.linalg.norm(window-center,axis=1)
    path_radius=float(radius.mean())
    radius_std=float(radius.std())
    radius_cv=radius_std/max(path_radius,1e-8)
    radius_slope=float(np.polyfit(np.arange(len(radius)),radius,1)[0]) if len(radius)>2 else 0.0
    half=len(window)//2
    centroid_drift=float(np.linalg.norm(window[half:].mean(axis=0)-window[:half].mean(axis=0)))
    centroid_drift_norm=centroid_drift/max(path_radius,1e-8)
    min_gap=max(4,len(window)//8)
    candidates=[np.linalg.norm(window[-1]-window[i]) for i in range(0,len(window)-min_gap)]
    nearest_return_dist=float(min(candidates)) if candidates else np.nan
    nearest_return_norm=nearest_return_dist/max(path_radius,1e-8)
    turning=0.0
    for i in range(1,len(window)-1):
        a=window[i]-window[i-1]; b=window[i+1]-window[i]
        na=np.linalg.norm(a); nb=np.linalg.norm(b)
        if na>1e-12 and nb>1e-12:
            turning += np.arccos(np.clip(np.dot(a,b)/(na*nb),-1,1))
    return {
        "path_length":path_length,
        "closure_gap":closure_gap,
        "closure_norm":closure_gap/max(path_radius,1e-8),
        "path_radius":path_radius,
        "radius_std":radius_std,
        "radius_cv":radius_cv,
        "radius_slope":radius_slope,
        "centroid_drift":centroid_drift,
        "centroid_drift_norm":centroid_drift_norm,
        "nearest_return_dist":nearest_return_dist,
        "nearest_return_norm":nearest_return_norm,
        "turning_total":float(turning),
    }

def build_window_table(trajs, window_size=64, stride=4, k_bars=8, tau_bar=0.035):
    rows=[]
    for tid,obj in trajs.items():
        xy=obj.xy if hasattr(obj,"xy") else obj["xy"]
        regime=obj.regime if hasattr(obj,"regime") else obj["regime"]
        difficulty=obj.difficulty if hasattr(obj,"difficulty") else obj["difficulty"]
        label=obj.label_loop if hasattr(obj,"label_loop") else obj["label_loop"]
        for start in range(0,len(xy)-window_size+1,stride):
            end=start+window_size
            w=xy[start:end]
            row={"traj_id":tid,"regime":regime,"difficulty":difficulty,"label_loop":label,"window_start":start,"window_end":end-1}
            row.update(baseline_geometry(w))
            row.update(encode_h1_profile(h1_diagram(w),w,k=k_bars,tau_bar=tau_bar))
            rows.append(row)
    return pd.DataFrame(rows)

def add_temporal_features(df, m=5, tau_bar=0.035):
    out=[]
    base=["topo_max","topo_top2_sum","topo_top3_sum","top2_over_top1","bar_entropy","n_bars_tau","closure_norm","radius_slope","centroid_drift_norm","nearest_return_norm"]
    for _,g in df.groupby("traj_id"):
        g=g.sort_values("window_end").copy()
        for col in base:
            vals=g[col].values.astype(float); means=[]; stds=[]
            for i in range(len(vals)):
                seg=vals[max(0,i-m+1):i+1]
                means.append(float(np.mean(seg))); stds.append(float(np.std(seg)))
            g[f"mean_{col}_last_m"]=means; g[f"std_{col}_last_m"]=stds
        active=(g["topo_max"].values>tau_bar).astype(float)
        multibar=(g["n_bars_tau"].values>=2).astype(float)
        frac_active=[]; frac_multi=[]; streak_active=[]; streak_multi=[]; tv=[]; ca=0; cm=0
        prof=g[["topo_max","topo_top2_sum","n_bars_tau","bar_entropy"]].values.astype(float)
        for i in range(len(g)):
            s=max(0,i-m+1)
            frac_active.append(float(np.mean(active[s:i+1]))); frac_multi.append(float(np.mean(multibar[s:i+1])))
            ca=ca+1 if active[i] else 0; cm=cm+1 if multibar[i] else 0
            streak_active.append(ca); streak_multi.append(cm)
            tv.append(0.0 if i==0 else float(np.mean([np.linalg.norm(prof[j]-prof[j-1]) for j in range(max(1,i-m+1),i+1)])))
        g["fraction_h1_active"]=frac_active; g["fraction_count_tau_ge_2"]=frac_multi
        g["current_h1_streak"]=streak_active; g["current_multibar_streak"]=streak_multi; g["profile_total_variation"]=tv
        topo=g["topo_max"].values; dec=[]; surv=[]
        for i in range(len(topo)):
            seg=topo[:i+1]; peak_i=int(np.argmax(seg)); peak=seg[peak_i]
            dec.append(float((peak-topo[i])/max(peak,1e-8))); surv.append(int(np.sum(topo[peak_i:i+1]>tau_bar)))
        g["post_peak_decay_rate"]=dec; g["h1_survival_after_peak"]=surv
        out.append(g)
    return pd.concat(out,ignore_index=True)

def add_rejection_flags_vnext1(df):
    df=df.copy()
    df["reject_transient"]=((df["post_peak_decay_rate"]>0.55)&(df["h1_survival_after_peak"]<3)).astype(int)
    df["reject_shrinking"]=((df["radius_slope"]<-0.004)&(df["post_peak_decay_rate"]>0.25)).astype(int)
    return df

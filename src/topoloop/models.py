from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

def fit_logreg(train_df, test_df, cols, seed=42):
    Xtr = train_df[cols].replace([np.inf, -np.inf], np.nan).fillna(0)
    Xte = test_df[cols].replace([np.inf, -np.inf], np.nan).fillna(0)
    ytr = train_df["label_loop"].values
    yte = test_df["label_loop"].values
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=3000, random_state=seed)),
    ])
    model.fit(Xtr, ytr)
    pred = model.predict(Xte)
    prob = model.predict_proba(Xte)[:, 1]
    return model, pred, prob, accuracy_score(yte, pred)

def fit_binary_models(train_df, test_df, feature_sets, seed=42):
    out = {}
    for name, cols in feature_sets.items():
        model, pred, prob, acc = fit_logreg(train_df, test_df, cols, seed)
        out[name] = {"model": model, "pred": pred, "prob": prob, "accuracy": acc}
    return out

def per_regime_table(test_df, predictions):
    rows = []
    for model_name, pred in predictions.items():
        tmp = test_df.copy()
        tmp["pred"] = pred
        for regime, g in tmp.groupby("regime"):
            label = int(g["label_loop"].iloc[0])
            rows.append({
                "model": model_name,
                "regime": regime,
                "accuracy": (g["pred"].values == g["label_loop"].values).mean(),
                "TPR_if_loop": g["pred"].mean() if label == 1 else np.nan,
                "FPR_if_nonloop": g["pred"].mean() if label == 0 else np.nan,
                "n_windows": len(g),
            })
    return pd.DataFrame(rows)

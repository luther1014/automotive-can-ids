"""Model training and leakage-aware validation and evaluation."""
from pathlib import Path
import json
import warnings
import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, confusion_matrix,
                             precision_score, recall_score, f1_score,
                             accuracy_score, roc_auc_score)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from .features import frame_features, FEATURE_NAMES
from .io import load_sample


def make_models():
    return {
        "dummy": Pipeline([("fill", SimpleImputer(strategy="constant", fill_value=-1)),
                           ("model", DummyClassifier(strategy="most_frequent"))]),
        "logistic_regression": Pipeline([
            ("fill", SimpleImputer(strategy="constant", fill_value=-1)),
            ("scale", StandardScaler()),
            ("model", LogisticRegression(max_iter=400, class_weight="balanced"))]),
        "random_forest": Pipeline([
            ("fill", SimpleImputer(strategy="constant", fill_value=-1)),
            ("model", RandomForestClassifier(
                n_estimators=80, max_depth=12, min_samples_leaf=5,
                class_weight="balanced_subsample", n_jobs=-1, random_state=42))]),
    }


def score(model, X, y):
    pred = model.predict(X)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    result = {
        "rows": int(len(y)), "positives": int(np.sum(y)),
        "attack_prevalence": float(np.mean(y)),
        "accuracy": float(accuracy_score(y, pred)),
        "precision": float(precision_score(y, pred, zero_division=0)),
        "recall": float(recall_score(y, pred, zero_division=0)),
        "f1": float(f1_score(y, pred, zero_division=0)),
        "false_positive_rate": float(fp / (fp + tn)) if fp + tn else None,
        "tp": int(tp), "tn": int(tn), "fp": int(fp), "fn": int(fn),
    }
    if len(np.unique(y)) == 2 and hasattr(model, "predict_proba"):
        scores = model.predict_proba(X)[:, 1]
        result["average_precision"] = float(average_precision_score(y, scores))
        result["roc_auc"] = float(roc_auc_score(y, scores))
    else:
        result["average_precision"] = None
        result["roc_auc"] = None
    return result


def _save_json(obj, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def validate_group_split(df):
    if df["source_file"].nunique() < 2:
        raise ValueError("Need at least two distinct training CSV captures for group validation")
    splitter = GroupShuffleSplit(n_splits=40, test_size=0.25, random_state=42)
    for train_idx, val_idx in splitter.split(df, df["attack"], groups=df["source_file"]):
        if df.iloc[train_idx]["attack"].nunique() == 2 and df.iloc[val_idx]["attack"].nunique() == 2:
            return train_idx, val_idx
    raise ValueError(
        "Could not find an internal capture-held-out validation split with both classes. "
        "This can happen with very small samples; increase --fraction or inspect capture distribution."
    )


def train(data_root, fraction, out, model_dir):
    print("Loading training sample...")
    df = load_sample(data_root, "train_01", fraction=fraction)
    print(f"Rows: {len(df):,}; attack prevalence: {df.attack.mean():.2%}; "
          f"captures: {df.source_file.nunique()}")
    train_idx, val_idx = validate_group_split(df)
    X = frame_features(df)
    y = df["attack"].to_numpy()
    results = {
        "note": "EXPLORE ONLY: sampled rows and capture-held-out internal validation; not thesis-final evaluation",
        "train_fraction": fraction,
        "feature_names": FEATURE_NAMES,
        "validation_files": sorted(df.iloc[val_idx].source_file.unique().tolist()),
        "train_files": sorted(df.iloc[train_idx].source_file.unique().tolist()),
        "models": {},
    }
    Path(model_dir).mkdir(parents=True, exist_ok=True)
    for name, model in make_models().items():
        print(f"Fitting {name}...")
        model.fit(X.iloc[train_idx], y[train_idx])
        metrics = score(model, X.iloc[val_idx], y[val_idx])
        results["models"][name] = metrics
        print(f" {name}: F1={metrics['f1']:.3f} recall={metrics['recall']:.3f} "
              f"FPR={metrics['false_positive_rate']}")
        # Persist fitted training-only model for validation inspection (not test evaluation).
        joblib.dump(model, Path(model_dir) / f"{name}.joblib")
    _save_json(results, out)
    print(f"Validation metrics -> {out}")
    print("Now evaluate these models on the 4 untouched test subsets.")


def evaluate(data_root, fraction, out, model_dir, splits):
    result = {
        "note": "SAMPLED TEST RESULTS: exploratory only; use fraction=1 for full held-out evaluation",
        "test_fraction": fraction, "splits": {},
    }
    models = {}
    for name in make_models():
        f = Path(model_dir) / f"{name}.joblib"
        if not f.exists():
            raise FileNotFoundError(f"Missing fitted model {f}; run 'canids train' first")
        models[name] = joblib.load(f)  # Only load models you generated yourself.
    for split in splits:
        print(f"Evaluating {split}...")
        df = load_sample(data_root, split, fraction=fraction, seed=2026)
        X = frame_features(df)
        y = df.attack.to_numpy()
        result["splits"][split] = {}
        for name, model in models.items():
            metric = score(model, X, y)
            result["splits"][split][name] = metric
            print(f" {name}: F1={metric['f1']:.3f}; recall={metric['recall']:.3f}; "
                  f"FPR={metric['false_positive_rate']}")
    _save_json(result, out)
    print(f"Test metrics -> {out}")

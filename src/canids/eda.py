"""First-pass dataset inspection and visual exploration."""
from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from .io import load_sample
from .features import frame_features


def inspect(data_root, split, fraction, output):
    print(f"Inspecting {split} ({fraction:.2%} uniform sample)...")
    df = load_sample(data_root, split, fraction=fraction)
    feats = frame_features(df)
    counts = df.attack.value_counts().reindex([0, 1], fill_value=0)
    missing = {k: int(v) for k, v in df.isna().sum().items()}
    per_file = df.groupby("source_file").agg(
        frames=("attack", "size"), attack_ratio=("attack", "mean")
    ).reset_index()
    top_ids = feats["can_id"].value_counts().head(15)
    summary = {
        "split": split, "sampling_fraction": fraction, "sample_rows": len(df),
        "sample_attack_rate": float(df.attack.mean()),
        "sample_attack_counts": {"normal": int(counts[0]), "attack": int(counts[1])},
        "sample_distinct_ids": int(feats["can_id"].nunique()),
        "missing_original_fields": missing,
        "unparseable_ids": int(feats.can_id.isna().sum()),
        "invalid_payloads": int(feats.dlc.isna().sum()),
        "per_file": per_file.to_dict(orient="records"),
        "top_ids_hex": [{"id": hex(int(k)), "sample_frames": int(v)} for k, v in top_ids.items()],
    }
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{split}_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    per_file.to_csv(out / f"{split}_capture_summary.csv", index=False)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["Normal frame", "Injected frame"], counts.values)
    ax.set_ylabel("Frames in random sample")
    ax.set_title(f"Label distribution — {split}")
    fig.tight_layout()
    fig.savefig(out / f"{split}_class_counts.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4))
    labels = [hex(int(x)) for x in top_ids.index]
    ax.bar(labels, top_ids.values)
    ax.tick_params(axis="x", rotation=45)
    ax.set_ylabel("Frames in random sample")
    ax.set_title(f"Most frequent CAN IDs — {split}")
    fig.tight_layout()
    fig.savefig(out / f"{split}_top_ids.png", dpi=150)
    plt.close(fig)

    print(json.dumps({k: v for k, v in summary.items() if k != "per_file"}, indent=2))
    print(f"Reports and plots saved in {out}")

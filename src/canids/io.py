"""Read the original four-column can-train-and-test CSV files safely in chunks."""
from pathlib import Path
import numpy as np
import pandas as pd

COLUMNS = ["timestamp", "arbitration_id", "data_field", "attack"]
SPLITS = (
    "train_01",
    "test_01_known_vehicle_known_attack",
    "test_02_unknown_vehicle_known_attack",
    "test_03_known_vehicle_unknown_attack",
    "test_04_unknown_vehicle_unknown_attack",
)


def files_for_split(root: str | Path, split: str) -> list[Path]:
    if split not in SPLITS:
        raise ValueError(f"Unknown split {split}. Expected one of {SPLITS}")
    root = Path(root).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Dataset root does not exist: {root}")
    paths = sorted(
        p for p in root.rglob("*.csv")
        if split in p.relative_to(root).parts[:-1]
    )
    if not paths:
        raise FileNotFoundError(
            f"No .csv files found within '{split}' under '{root}'. "
            "Point --data-root to the extracted set_01 directory, "
            "and check the original train_01/test_XX folder names."
        )
    return paths


def csv_has_header(path: Path) -> bool:
    with path.open("r", encoding="utf-8-sig") as fp:
        first = fp.readline().strip().lower().replace('"', "")
    fields = [x.strip() for x in first.split(",")]
    return fields == COLUMNS


def load_sample(root: str | Path, split: str, fraction: float = 0.02,
                seed: int = 42, chunksize: int = 100_000) -> pd.DataFrame:
    """Uniform Bernoulli sample across *rows*, preserving capture provenance.

    Scans each original CSV file without loading the complete dataset in RAM.
    The fraction is approximate; for publication metrics evaluate full test traces.
    """
    if not 0 < fraction <= 1:
        raise ValueError("fraction must be in (0, 1]")
    rng = np.random.default_rng(seed)
    parts = []
    paths = files_for_split(root, split)
    root = Path(root).expanduser().resolve()
    for path in paths:
        header = csv_has_header(path)
        print(f"  reading {path.relative_to(root)}")
        reader = pd.read_csv(
            path, header=None, names=COLUMNS, skiprows=1 if header else 0,
            dtype={"arbitration_id": "string", "data_field": "string", "attack": "string"},
            chunksize=chunksize, low_memory=False,
        )
        for chunk in reader:
            keep = rng.random(len(chunk)) < fraction
            if keep.any():
                sample = chunk.loc[keep].copy()
                sample["source_file"] = path.relative_to(root).as_posix()
                parts.append(sample)
    if not parts:
        raise ValueError("Sample is empty. Increase --fraction.")
    result = pd.concat(parts, ignore_index=True)
    result["timestamp"] = pd.to_numeric(result["timestamp"], errors="coerce")
    result["attack"] = pd.to_numeric(result["attack"], errors="raise")
    if result["attack"].isna().any() or not result["attack"].isin([0, 1]).all():
        raise ValueError("attack must be binary 0/1 (no nulls)")
    result["attack"] = result["attack"].astype("int8")
    return result

"""Stateless frame-level CAN feature extraction for baseline classifiers.

NOTE: Can IDs are hexadecimal even when they contain only digits: '191' means 0x191.
Do not include labels, source filenames or absolute timestamps as ML predictors.
"""
import numpy as np
import pandas as pd

FEATURE_NAMES = ["can_id", "dlc", *(f"byte_{i}" for i in range(8))]


def can_id_to_int(value):
    if pd.isna(value):
        return np.nan
    s = str(value).strip()
    try:
        v = int(s, 16)
    except ValueError:
        return np.nan
    return float(v) if 0 <= v <= 0x1FFFFFFF else np.nan


def payload_to_bytes(value):
    if pd.isna(value):
        return None
    s = str(value).strip().replace(" ", "")
    if len(s) > 16 or len(s) % 2 != 0:
        return None
    try:
        b = bytes.fromhex(s)
    except ValueError:
        return None
    return list(b)


def frame_features(df: pd.DataFrame) -> pd.DataFrame:
    ids = df["arbitration_id"].map(can_id_to_int).to_numpy(dtype="float64")
    payloads = df["data_field"].map(payload_to_bytes)
    dlcs = np.full(len(df), np.nan, dtype="float32")
    byte_arr = np.full((len(df), 8), -1.0, dtype="float32")
    for i, value in enumerate(payloads):
        if value is not None:
            dlcs[i] = len(value)
            byte_arr[i, :len(value)] = value
    data = {"can_id": ids, "dlc": dlcs}
    data.update({f"byte_{i}": byte_arr[:, i] for i in range(8)})
    return pd.DataFrame(data, columns=FEATURE_NAMES)

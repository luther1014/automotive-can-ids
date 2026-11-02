"""Generates a beginner notebook. Run once to regenerate notebooks/01_eda.ipynb."""
import json
from pathlib import Path

def md(content):
    return {'cell_type': 'markdown', 'metadata': {}, 'source': content.splitlines(True)}

def py(content):
    return {'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 'source': content.splitlines(True)}

cells = [
md('''# 01 — Exploring `set_01` CAN traffic

**Goal:** Find out what each field means and whether basic data patterns differ between normal and injected frames. Run this from the project root with `jupyter lab`. The notebook reads a random *sample* by scanning CSVs in chunks. Raw data must stay unchanged.\n'''),
py('''from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from canids.io import load_sample
from canids.features import frame_features

ROOT = Path("data/raw/can-train-and-test/set_01")
FRACTION = 0.02   # ~2% of training frames; increase if necessary
train = load_sample(ROOT, "train_01", fraction=FRACTION)
train.head()
'''),
md('''## 1. Schema and sample sizes

Check for missing values, data types and the class distribution. For the original dataset, `attack=1` means an injected CAN frame, not necessarily an entire capture under attack.\n'''),
py('''print(train.dtypes)
print(train.shape)
print(train.isna().sum())
print(train.attack.value_counts())
print(train.attack.value_counts(normalize=True).rename('fraction'))
'''),
md('''**Interpret:** Can accuracy be misleading if the dataset is dominated by attack-free frames? What happens when a model predicts `0` for every frame?'''),
py('''counts = train.attack.value_counts().reindex([0,1], fill_value=0)
counts.rename({0:'Normal frame', 1:'Injected frame'}).plot.bar(title='Label distribution')
plt.ylabel('Frames in sample'); plt.show()
'''),
md('''## 2. Convert hexadecimal CAN IDs and payload bytes

An ID like `191` is hexadecimal (0x191), **not** decimal 191. Missing bytes are encoded as -1 for our starter; `dlc` is derived from payload string length. Absolute time, filenames and label are **not** predictive features.\n'''),
py('''X = frame_features(train)
print(X.head())
print(X.describe().T)
print('Distinct IDs:', X.can_id.nunique())
print('Invalid IDs:', X.can_id.isna().sum())
print('Invalid payloads:', X.dlc.isna().sum())
'''),
md('''## 3. Common IDs, payload lengths and labels

A particular ID being associated with injected frames is a useful starting observation, but can also be a dataset-specific shortcut. It is *not* evidence that the same ID is malicious in every vehicle.\n'''),
py('''top = X.can_id.value_counts().head(15)
top.index = [hex(int(i)) for i in top.index]
top.plot.bar(title='Most frequent CAN IDs'); plt.ylabel('Sample frames'); plt.show()

joined = X.assign(attack=train.attack.to_numpy())
print(pd.crosstab(joined.dlc, joined.attack, normalize='index').round(3))
'''),
md('''## 4. Compare capture files — crucial for leakage

Each source CSV contains a trace. Do not create a row-level random train/validation split if the same capture appears on both sides. Examine how many files are entirely normal or dominated by attacks.\n'''),
py('''per_file = train.groupby('source_file').attack.agg(['size','sum','mean'])
per_file.columns = ['sample_frames', 'attack_frames', 'attack_ratio']
display(per_file.sort_values('attack_ratio', ascending=False).head(30))
'''),
md('''## 5. Timing exploration (not yet an ML feature)

Only compute time deltas *within each capture*. Start with one trace. A high rate or near-zero time delta can indicate injected traffic, but CAN IDs normally have different frequencies and timestamp recording may add artifacts.\n'''),
py('''source = train.source_file.iloc[0]
trace = train[train.source_file == source].sort_values('timestamp')
interval = trace.timestamp.diff().dropna()
print('Capture:', source)
print(interval.describe(percentiles=[.5,.9,.99]))
interval.clip(lower=0, upper=0.2).hist(bins=40)
plt.title('Inter-frame gaps (sampled frames: gaps are distorted)')
plt.xlabel('Seconds between sampled frames'); plt.show()
'''),
md('''> **Warning:** This notebook samples frames. Sampling distorts inter-arrival intervals, so these timing plots are just sanity checks! For valid timing analysis later, read complete, correctly ordered captures and compute strictly causal features before any frame downsampling.\n
## Questions for your research log

1. What is the attack prevalence, and what does it imply for accuracy?
2. Which CAN IDs occur most often? Do they belong to normal or injected frames?
3. Are payload lengths identical across benign and attack frames?
4. Is the label distribution similar across capture files?
5. What would happen if you trained only on frame content and then tested a different vehicle?
6. Which new feature would you add to detect DoS or spoofing?\n''')
]
nb = {'cells': cells, 'metadata': {'kernelspec': {'display_name':'Python 3','language':'python','name':'python3'}, 'language_info': {'name':'python'}}, 'nbformat':4,'nbformat_minor':5}
out=Path('notebooks/01_eda.ipynb')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(nb,indent=1),encoding='utf-8')
print(f'Wrote {out}')

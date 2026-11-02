# Automotive CAN IDS — learning starter

A **starter**, not a thesis-final IDS, for the ORIGINAL Brooke Lampe & Weizhi Meng
`can-train-and-test` dataset (`set_01`). It is not the separately released v1.5 variant.

Sources:
- Paper: https://doi.org/10.1016/j.cose.2024.103777
- Dataset: https://data.dtu.dk/articles/dataset/can-train-and-test/24805533

## Setup (Linux/macOS/WSL)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests
```

Download and extract the original dataset *separately*. Place its `set_01` directory at:
`data/raw/can-train-and-test/set_01/`.
There should be five directories named `train_01`, `test_01_known_vehicle_known_attack`,
`test_02_unknown_vehicle_known_attack`, `test_03_known_vehicle_unknown_attack`,
`test_04_unknown_vehicle_unknown_attack`. They may have nested capture folders;
this loader recursively searches for CSVs inside each designated split.
Do not put original CSVs in Git.

## Optional synthetic smoke test (clearly **not** scientific data)

```bash
python scripts/make_synthetic_demo.py
canids inspect --data-root data/synthetic/set_01 --fraction 1.0
canids train --data-root data/synthetic/set_01 --fraction 1.0
canids evaluate --data-root data/synthetic/set_01 --fraction 1.0
```

## First real experiments

```bash
canids inspect --data-root data/raw/can-train-and-test/set_01 --fraction 0.02
canids train --data-root data/raw/can-train-and-test/set_01 --fraction 0.02
canids evaluate --data-root data/raw/can-train-and-test/set_01 --fraction 0.005
```

Start with the author-provided test_01 if you prefer:

```bash
canids evaluate --data-root data/raw/can-train-and-test/set_01 --fraction 0.005 --splits test_01_known_vehicle_known_attack
```

Outputs: `results/figures/` has EDA plots and capture summaries;
`results/metrics/` has validation and per-scenario test JSON;
`models/` has fitted scikit-learn models.

**Caution:** Uniform Bernoulli row sampling is for quick exploration, not publishable
performance estimates. Scan all CSVs but only retain a fraction of their rows.
For final held-out results, use `--fraction 1.0` *only if memory permits*, or implement
streaming per-capture scoring. Changing the fraction changes the sample and
can hide rare attacks. Features deliberately exclude absolute timestamps and
file names to avoid obvious data leakage. Captures are kept separate during
internal validation, but train/validation captures may still share driving
patterns and capture artifacts; investigate further before claiming robustness.

Model label semantics are **injected frame** (1) vs **non-injected frame** (0),
not whether the *entire vehicle capture* was under attack. The starter's
features are memoryless per-frame features; timing-based IDS is future work.

Models: Dummy (sanity check), logistic regression, random forest.
No GPU required. Neither a raw-CAN reader nor embedded deployment is included.

If your CSVs have a different schema or directory naming than the original,
inspect one file and adapt `io.py`; do not silently treat different formats as
identical. `set_01` training must not be mixed with any of the four tests.

## Guided learning

- Start with `notebooks/01_eda.ipynb` in Jupyter Lab after installing `jupyterlab`.
- Use `docs/experiment-plan.md` as the research checklist.
- Write notes in `docs/research-log.md` and record key design choices in `docs/decisions.md`.
- `scripts/make_synthetic_demo.py` exists solely for testing that the pipeline executes.
- `scripts/create_notebook.py` regenerates the guided notebook.

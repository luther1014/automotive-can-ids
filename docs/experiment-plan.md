# Experiment plan (progressive difficulty)

## Experiment 0 — learn the data
- Use `canids inspect` for train_01 and test_01 at 2% and 0.5% respectively.
- Read a few original CSV lines to verify column names, no-header/header, hex ID and payload.
- Determine class ratio, unique IDs, per-file label composition, malformed rows.
- Check *within each capture* for time monotonicity, timing gaps, and traffic bursts.
- Do **not** drop repeated frames: repeated CAN transmissions are often legitimate.

## Experiment 1 — frame-only baseline
- Features: numeric CAN ID, DLC, each of eight payload bytes. No label, filename, timestamp.
- Dummy, logistic regression, random forest.
- Hold out entire training capture files for validation.
- Evaluate test_01 only after models are fitted and not selected on test results.
- Record F1, attack recall, precision, false positive rate, confusion matrix, PR-AUC.

## Experiment 2 — generalization
- Freeze model and preprocessing; evaluate test_02, test_03, test_04 unchanged.
- Compare unknown-vehicle vs unknown-attack degradation, confusion matrix counts.
- Observe unseen arbitration IDs per scenario; try sensitivity analysis with ID withheld.
- The dataset label identifies *injected frames*, not necessarily attack-affected vehicle states.

## Experiment 3 — causal time/context features
- Within a single capture, sorted by timestamp, derive prior inter-arrival interval
  for the same CAN ID, counts in trailing time window, rolling ID entropy, etc.
- Ensure time features are derived only from previously observed CAN frames.
- Assess generalization, latency, feature-store memory; compare to frame-only baseline.
- Do not concatenate timestamps across captures or compute future-looking statistics.

## Experiment 4 — embedded deployment
- Select suitable model after accuracy/resource tradeoff comparisons.
- Specify target hardware and throughput; extract identical features on the device.
- Profile model size, peak RAM, median and p99 per-frame inference time,
  CPU utilization and effective false alerts per minute or hour of capture.
- Replay recorded traces using correct replay infrastructure, or start from
  CSV-fed inference benchmark before physical CAN replay.

## Scientific precautions
- No train/test cross-contamination; no test-set hyperparameter search.
- Do not compare sampled rates as if they were full-corpus metrics.
- Normalize features using training only; pipeline takes care of this.
- Cross-vehicle generalization might be compromised by CAN-ID differences.
- Very low prevalence means high accuracy is potentially meaningless.
- Note the data collection source, capture conditions, and dataset version.

# Research log

## YYYY-MM-DD – First can-train-and-test experiment
- **Research question:** Can simple frame-level features detect injected CAN frames?
- **Dataset:** can-train-and-test original release, set_01; note version and source URL
- **Environment:** Python version, OS, CPU, RAM
- **Split strategy:** Author's train/test folders; internal validation held out by capture file
- **Sampling:** Training %, evaluation %; RNG seed; labels not stratified for test
- **Features:** Numeric hex ID, DLC, 8 payload bytes; no timestamp / provenance features
- **Models and parameters:** Dummy, logistic regression, random forest
- **Results:** (attach JSON metrics)
- **Unexpected observations:**
- **Threats to validity:** Sampled frame-level metrics, overlapping vehicle semantics
- **Next experiment:**

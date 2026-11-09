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

### Experiment 01 — Initial EDA of CAN Train and Test, Set 01

**Objective:** Understand CAN frame structure, label distribution, data quality and initial patterns before ML model development.

**Dataset:** can-train-and-test, `set_01`, training subset.

**Method:** Randomly sampled approximately 2% of training frames across 12 CSV captures.

**Findings:**

- Analyzed 212,897 sampled CAN frames.
- Identified 211,885 non-injected frames (99.52%) and 1,012 injected frames (0.48%).
- Observed 52 distinct arbitration identifiers.
- Found no missing values or invalid CAN ID/payload conversions in the sample.
- Observed payload lengths between 2 and 8 bytes.
- Approximately 71.4% of sampled attack frames came from the two DoS captures.
- Observed substantial differences in attack prevalence between capture files.

**Interpretation:** The training sample exhibits significant class imbalance and unequal representation of attacks across captures. Consequently, classification accuracy alone is insufficient. Future experiments should emphasize precision, recall, F1-score, false-positive rates and performance across different attack scenarios.

**Limitations:** Results are based on a 2% sample. Timing measurements from randomly sampled frames do not represent actual inter-frame intervals.

**Next step:** Examine the relationship between CAN identifiers and attack labels, followed by training a simple baseline classifier with capture-aware validation.

Initial CAN ID analysis revealed that all 1,012 sampled injected frames were associated with four arbitration identifiers (0x000, 0x0C1, 0x0C9, and 0x1F5). While identifier 0x000 appeared exclusively in injected frames within the sample, the remaining identifiers occurred predominantly in normal traffic. This suggests that CAN ID alone may be insufficient for detecting certain attacks and motivates evaluating additional payload-based features.

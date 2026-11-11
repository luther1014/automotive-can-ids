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

# Research Log — Machine Learning-Based Automotive CAN Intrusion Detection

**Project:** Intrusion Detection in Automotive Computing Systems  
**Dataset:** CAN Train and Test — `set_01`  
**Research focus:** Machine learning-based CAN intrusion detection, model generalization and future embedded deployment  
**Last updated:** 9 November 2026  
**Status:** Initial baseline experiments and error analysis completed

---

## Experiment 01 — Dataset Exploration and Preprocessing

**Date:** 8 November 2026

### Objective

Understand the structure, characteristics and label distribution of the CAN Train and Test dataset before training machine learning models.

### Methodology

- Loaded a 2% random sample from the `train_01` subset.
- Analyzed CAN arbitration identifiers, payloads, labels and source captures.
- Converted hexadecimal CAN identifiers and payload bytes into numerical representations.
- Examined class imbalance, frequent CAN identifiers and capture-level attack distributions.

### Results

| Property                         | Observation      |
| -------------------------------- | ---------------- |
| Frames analyzed                  | 212,897          |
| Source captures                  | 12               |
| Unique CAN IDs                   | 52               |
| Normal frames                    | 211,885 (99.52%) |
| Injected frames                  | 1,012 (0.48%)    |
| Missing or invalid parsed values | 0 in the sample  |
| Observed payload lengths         | 2–8 bytes        |

All sampled injected frames were associated with four CAN identifiers:

| CAN ID  | Injected frames | Total frames |
| ------- | --------------: | -----------: |
| `0x0C1` |             528 |       16,669 |
| `0x000` |             195 |          195 |
| `0x0C9` |             155 |       11,738 |
| `0x1F5` |             134 |        6,081 |

The two DoS training captures accounted for 723 of the 1,012 sampled injected frames (71.4%).

### Interpretation

1. The training data is highly imbalanced. Accuracy alone is unsuitable for evaluating attack detection.
2. Certain CAN identifiers contain both injected and normal frames, indicating that identifiers alone may not be sufficient for distinguishing attacks.
3. The observed concentration of injected frames in particular captures may influence what a model learns.
4. Timing statistics calculated after random frame sampling are not representative of actual inter-frame intervals.

### Outcome

The initial preprocessing pipeline was validated on the sample. Frame-level classification was selected as the first baseline approach.

---

## Experiment 02 — Baseline Model Training and Internal Validation

**Date:** 8 November 2026

### Objective

Establish initial supervised machine learning baselines using simple CAN frame features.

### Feature representation

Ten numerical features were used:

- CAN arbitration ID
- Payload length (`dlc`)
- Payload bytes `byte_0` through `byte_7`

Absolute timestamps and source filenames were excluded from predictive features.

### Models

1. Dummy Classifier
2. Logistic Regression
3. Random Forest

### Validation methodology

- Training data sampled at 2%.
- Internal validation performed using capture-level separation.
- The held-out validation captures were `DoS-1.csv`, `rpm-2.csv` and `standstill-1.csv`.
- Validation consisted of 57,366 frames, including 265 injected frames.

### Results

| Metric          |  Dummy | Logistic Regression | Random Forest |
| --------------- | -----: | ------------------: | ------------: |
| Accuracy        | 99.54% |              95.93% |        99.98% |
| Precision       |     0% |               9.93% |          100% |
| Recall          |     0% |              96.60% |        96.60% |
| F1-score        |     0% |              18.00% |        98.27% |
| False positives |      0 |               2,323 |             0 |
| False negatives |    265 |                   9 |             9 |

### Interpretation

The Dummy Classifier demonstrated that high accuracy can coexist with complete failure to detect attacks.

Logistic Regression achieved high recall but generated substantial false alarms at its default decision threshold.

Random Forest achieved excellent internal validation performance, detecting 256 of 265 injected frames without false positives.

However, this result was obtained using attack categories also represented in the training captures. It does not demonstrate robustness to unseen vehicles or attack types.

### Outcome

Random Forest was selected as the strongest initial baseline for further investigation, without treating it as the final model.

---

## Experiment 03 — Generalization Across Official Test Scenarios

**Date:** 9 November 2026

### Objective

Investigate how the baseline models perform under different vehicle and attack familiarity conditions.

### Methodology

Evaluated the previously trained models on a 0.5% random sample from each of the four official test scenarios.

### Random Forest results

| Scenario                                  | Attack frames | Recall | F1-score | False positives |
| ----------------------------------------- | ------------: | -----: | -------: | --------------: |
| Test 01 — Known vehicle, known attack     |           321 | 33.33% |   50.00% |               0 |
| Test 02 — Unknown vehicle, known attack   |           811 |  5.06% |    8.94% |              65 |
| Test 03 — Known vehicle, unknown attack   |            88 |     0% |       0% |               0 |
| Test 04 — Unknown vehicle, unknown attack |            71 |  1.41% |    2.08% |              24 |

### Interpretation

The substantial difference between internal validation and official testing suggests that the model has learned patterns that do not generalize consistently.

Detection performance deteriorated under vehicle changes, unfamiliar attacks and even some familiar test recordings.

Potential explanations include:

- Dependence on vehicle-specific CAN identifiers or payload characteristics.
- Insufficient representation of attack variations during training.
- Differences in capture conditions.
- Limitations of stateless frame-level features.
- Effects of sparse sampling and relatively few attack observations.

These explanations remain hypotheses requiring additional investigation.

### Outcome

Generalization was identified as a central research challenge.

---

## Experiment 04 — Capture-Level Error Analysis

**Date:** 9 November 2026

### Objective

Identify which specific recordings explain the reduced detection performance in Test 01.

### Methodology

Analyzed the Random Forest's predictions separately for each capture in `test_01_known_vehicle_known_attack`.

### Results

| Capture               | Injected frames | Detected | Missed |
| --------------------- | --------------: | -------: | -----: |
| DoS-3                 |              92 |       92 |      0 |
| DoS-4                 |             200 |        0 |    200 |
| RPM-3                 |              13 |        0 |     13 |
| RPM-4                 |               1 |        0 |      1 |
| Force-neutral-3 and 4 |               8 |        8 |      0 |
| Standstill-3 and 4    |               7 |        7 |      0 |

All 214 missed attack frames came from DoS-4 and the two RPM recordings. DoS-4 alone accounted for approximately 93.5% of the missed attacks.

### Interpretation

Performance varies substantially between recordings belonging to the same attack category.

In particular, complete detection of DoS-3 contrasts with complete failure on DoS-4.

This suggests that the model may depend on characteristics specific to certain attack recordings rather than learning a general representation of the DoS category.

### Outcome

DoS-3 and DoS-4 were selected for further exploratory feature comparison.

---

## Experiment 05 — DoS Arbitration ID Investigation

**Date:** 9 November 2026

### Objective

Determine whether different arbitration identifiers explain the detection discrepancy between DoS-3 and DoS-4.

### Results

| Capture | Injected CAN ID | Injected frames | Detected |
| ------- | --------------- | --------------: | -------: |
| DoS-3   | `0x0C1`         |              92 |       92 |
| DoS-4   | `0x0C1`         |             200 |        0 |

### Interpretation

Both sampled DoS recordings use the same CAN identifier.

Therefore, differences in the identifiers used by these two recordings cannot explain their detection discrepancy.

Because the baseline model uses CAN ID, payload length and payload bytes, payload characteristics are a plausible explanation for the differing predictions.

However, payload values have not yet been compared, so this explanation is not confirmed.

### Updated hypothesis

**H1:** The Random Forest may have learned specific payload patterns associated with injected frames, causing its detection performance to depend on differences between individual DoS recordings.

### Outcome

CAN identifier mismatch was ruled out as the direct explanation for this particular DoS-3 versus DoS-4 discrepancy.

Payload and feature-distribution comparisons remain necessary.

---

## Methodological Limitations Identified So Far

1. **Sampling:** Training and testing used 2% and 0.5% samples, respectively. Results are exploratory rather than final full-dataset performance estimates.
2. **Class imbalance:** Injected frames represent a small fraction of total traffic, making accuracy and some other metrics potentially misleading.
3. **Validation coverage:** A single capture-level split may not adequately represent variation across recordings.
4. **Generalization:** A model may learn characteristics specific to the vehicle, attack implementation or capture session.
5. **Feature limitations:** The current approach treats each frame independently and does not incorporate message timing or temporal context.
6. **Test-set exposure:** Official test results have already been examined for exploratory diagnosis. Subsequent model development should rely on training-derived validation data rather than repeatedly optimizing against these test scenarios.
7. **Label interpretation:** The binary target identifies injected frames; it does not necessarily indicate whether a complete capture or vehicle operating state was affected by an attack.

---

## Next Planned Experiments

### Immediate: Explain the DoS Detection Difference

- Compare payload values and lengths between DoS-3 and DoS-4.
- Compare their attack-frame features with those from training captures DoS-1 and DoS-2.
- Examine whether missed attack frames have feature combinations absent from training.

### Next: Feature Ablation

Train and compare three configurations using training-derived validation:

- CAN ID only
- Payload length and bytes only
- CAN ID, payload length and bytes combined

The objective is to quantify the contribution of each feature group.

### Later: Improved Generalization

- Evaluate multiple capture-held-out validation partitions.
- Investigate training-set coverage and sampling strategies.
- Introduce causal temporal features.
- Consider lightweight anomaly detection approaches.
- Compare accuracy, false alarms and embedded resource requirements.

---

## Current Research Direction

**Working research question:**

_How effectively do lightweight machine learning models detect injected automotive CAN frames across different attack recordings, attack types and vehicle platforms, and can improved feature representations increase generalization while remaining suitable for embedded deployment?_

**Current conclusion:**

Initial Random Forest results demonstrate strong performance on selected held-out training captures but substantially weaker performance across the official test scenarios. Follow-up analysis identified major differences between recordings within the same attack category. These findings motivate more systematic investigation of feature dependence, training coverage and cross-scenario generalization.

**Important:** These are preliminary observations, not final thesis conclusions.

### Experiment 06 — Payload-Level Investigation of DoS Detection

**Date:** 9 November 2026

**Objective:** Determine whether differences in CAN payload characteristics explain the detection discrepancy between DoS-3 and DoS-4.

**Method:** Compared the arbitration identifiers, payload lengths and injected payload values in the sampled DoS-3 and DoS-4 test recordings.

**Results:**

| Property                | DoS-3              | DoS-4              |
| ----------------------- | ------------------ | ------------------ |
| CAN ID                  | `0x0C1`            | `0x0C1`            |
| Payload length          | 8 bytes            | 8 bytes            |
| Injected payload        | `0000000000000000` | `2026662920DA1D72` |
| Sampled injected frames | 92                 | 200                |
| Detected                | 92                 | 0                  |

**Interpretation:** Both recordings use identical CAN identifiers and payload lengths, but their injected payload values differ. Because the classifier uses CAN ID, payload length and payload bytes, the differing payload representations are a plausible explanation for the different predictions.

**Hypothesis:** The classifier may rely on learned payload patterns that are not robust to variations of the same attack category.

**Limitation:** The model's learned decision rules and the distribution of these payloads in the training data have not yet been examined. Therefore, payload memorization remains a hypothesis rather than a confirmed explanation.

**Next step:** Compare the two test payloads against the training DoS captures and investigate whether temporal features could improve detection of attacks missed by frame-level classification.

### Experiment 07 — Training-Set Payload Comparison

**Date:** 9 November 2026

**Objective:** Investigate whether the payload differences between DoS-3 and DoS-4 correspond to patterns observed during Random Forest training.

**Methodology:** Examined injected frames associated with CAN ID `0x0C1` in the 2% training sample and compared their payload values with the two DoS test recordings.

**Results:**

- The sampled training data contained 528 injected frames with CAN ID `0x0C1` and payload `0000000000000000`, all from DoS-2.
- The alternative payload `2026662920DA1D72` was not observed among sampled training attack frames with this identifier.
- DoS-3 used the same injected payload as DoS-2 and achieved 100% attack recall in the sampled test.
- DoS-4 used the alternative payload and achieved 0% attack recall.

**Interpretation:** The results provide evidence that Random Forest detection is sensitive to payload characteristics encountered during training. The model detects a familiar payload pattern but fails on the observed alternative payload, despite the CAN identifier, payload length and attack category being the same.

**Limitations:** The results do not establish which individual payload bytes or decision-tree rules determine classification. The analysis also does not establish whether the alternative payload occurs among normal training frames or in the unsampled training data.

**Research implication:** This finding motivates controlled feature-ablation experiments and investigation of causal temporal features, which could help detect abnormal message injection without relying exclusively on individual frame payload values.

**Next step:** Inspect model predictions and attack probabilities for the two payload representations, followed by training-only feature ablation and temporal analysis.

### Experiment 08 -

A controlled prediction experiment was performed using two CAN frames with identical arbitration IDs (0x0C1) and payload lengths (8 bytes), differing only in payload content. Random Forest assigned an attack score of 0.99828 to the all-zero payload and 0.00000 to the alternative payload 2026662920DA1D72. This demonstrates that payload-byte values influence the learned decision function. Combined with earlier training-set observations, the results support investigating payload-pattern dependence as a potential limitation of frame-level intrusion detection. Further analysis is required to determine whether the alternative payload appears in normal training traffic and which features drive the model's decisions.

### Experiment 08 — Final Training Payload Verification

**Date:** 9 November 2026

**Objective:** Examine whether the two DoS payload patterns appear in normal or injected frames of the original 2% training sample.

**Results:**

| Payload            | Normal frames | Injected frames |
| ------------------ | ------------: | --------------: |
| `0000000000000000` |            99 |             528 |
| `2026662920DA1D72` |             0 |               0 |

All comparisons concern CAN ID `0x0C1`.

**Interpretation:**

The all-zero payload occurs in both normal and injected traffic, demonstrating that identical frame-level feature vectors can correspond to different injection labels. Therefore, frame content alone cannot perfectly distinguish these observations.

The alternative DoS-4 payload was absent from the sampled training data. This is consistent with the model's failure to recognize DoS-4, but absence from the full training corpus has not been established.

A controlled experiment previously showed that changing only the payload from `0000000000000000` to `2026662920DA1D72` changed the Random Forest's predicted class from attack to normal, with reported attack scores of 0.99828 and 0.00000 respectively.

**Conclusion:** The baseline classifier exhibits payload-dependent detection behavior and limited generalization to the observed alternative DoS payload. This motivates feature-ablation experiments and future investigation of temporal communication features.

**Next experiment:** Compare CAN-ID-only, payload-only and combined-feature Random Forest classifiers under a consistent capture-held-out validation protocol.

### Experiment 09 — Complete Training Dataset Investigation

**Date:** 10 November 2026

**Objective:** Verify observations from the initial 2% sample against the complete `train_01` dataset and investigate the representation of the DoS-3 and DoS-4 payloads.

**Methodology:** Processed all training CSV files using chunked reading, accumulating CAN ID distributions, attack counts and payload frequencies without loading the entire dataset into memory.

**Findings:**

- The complete training set contains 49,557 injected frames across four CAN identifiers: `0x0C1`, `0x000`, `0x0C9` and `0x1F5`.
- All 25,954 injected frames with CAN ID `0x0C1` use payload `0000000000000000` and originate from `DoS-2.csv`.
- The same CAN ID and all-zero payload appear in 4,772 non-injected frames.
- The alternative DoS-4 payload `2026662920DA1D72` occurs once as a non-injected frame and never as an injected frame within the full training dataset.

**Interpretation:**

The overlap between injected and non-injected frames with identical feature representations demonstrates an inherent limitation of the current stateless classifier. Identical feature vectors cannot be assigned different predictions by a deterministic model.

The DoS-4 payload was absent from the original 2% model-fitting sample, although it occurred once in the complete training data. Its absence from sampled training attacks is consistent with the model's failure to recognize that attack payload.

**Limitations:** These findings do not prove payload memorization or demonstrate that temporal features will resolve the observed classification failures.

**Next steps:** Locate the single alternative-payload occurrence, perform controlled feature ablation using training-derived validation splits, and subsequently investigate causal temporal features.

The complete training dataset contained one non-injected occurrence of the DoS-4 payload in DoS-1.csv, at timestamp 1672531202.076127. This payload was absent from the 2% sample used for model fitting. The observation refines the earlier payload-generalization hypothesis but does not establish the model's internal decision mechanism. Further analysis will quantify the contribution of CAN identifiers and payload features through controlled feature ablation.

## Feature Ablation result

Metric RF-A: ID only RF-B: Payload only RF-C: Combined
Precision 2.83% 29.82% 100%
Recall 100% 73.58% 96.60%
F1-score 5.50% 42.44% 98.27%
Average precision 3.86% 30.20% 96.62%
False-positive rate 15.95% 0.80% 0%
True positives 265 195 256
False positives 9,110 459 0
False negatives 0 70 9

### Experiment 10 — Random Forest Feature Ablation

**Date:** 10 November 2026

**Objective:** Quantify the contribution of CAN arbitration identifiers and payload information to frame-level intrusion detection.

**Methodology:**

Three Random Forest classifiers were trained using the same 2% training sample, capture-held-out validation split, random seed and hyperparameters. Only the input feature groups differed.

- RF-A: CAN identifier only.
- RF-B: Payload length and eight payload bytes.
- RF-C: CAN identifier, payload length and eight payload bytes.

**Results:**

| Model | Precision | Recall | F1-score | False-positive rate |
| ----- | --------: | -----: | -------: | ------------------: |
| RF-A  |     2.83% |   100% |    5.50% |              15.95% |
| RF-B  |    29.82% | 73.58% |   42.44% |               0.80% |
| RF-C  |      100% | 96.60% |   98.27% |                  0% |

**Interpretation:**

CAN ID alone achieved perfect recall but produced excessive false positives, indicating that identifier-based classification is insufficient for distinguishing many injected frames from legitimate traffic.

Payload-only classification reduced false positives substantially but missed approximately 26.4% of injected frames.

Combining CAN ID and payload features yielded the highest F1-score, suggesting that these feature groups provide complementary information for classification.

**Limitations:**

The experiment used one capture-held-out validation partition and a 2% training sample. The excellent combined-model performance should not be interpreted as evidence of generalization, particularly given the poor results previously observed on the official testing scenarios.

**Next steps:**

1. Compare error distributions across individual validation captures.
2. Evaluate model robustness using multiple training-derived capture splits.
3. Examine sensitivity to training sample size.
4. Investigate causal temporal features as a potential way to reduce dependence on frame-specific payload patterns.

### Experiment 10 — Feature Ablation and Per-Capture Evaluation

**Date:** 10 November 2026

**Objective:** Investigate the relative contributions of CAN identifiers and payload features to frame-level attack detection.

**Method:** Three Random Forest models were trained with identical hyperparameters and capture-held-out validation, varying only the input feature groups.

**Overall results:**

| Model        | Precision | Recall |     F1 |
| ------------ | --------: | -----: | -----: |
| ID only      |     2.83% |   100% |  5.50% |
| Payload only |    29.82% | 73.58% | 42.44% |
| Combined     |      100% | 96.60% | 98.27% |

**Per-capture findings:**

- **DoS-1:** All three models detected all 195 sampled injected frames. The combined model produced no false positives.
- **RPM-2:** Only the ID-only model detected all nine sampled injected frames, but it generated 2,610 false positives. The other models missed all nine attacks.
- **Standstill-1:** The payload-only model missed all 61 injected frames, while the combined model detected all 61 without false positives.

**Interpretation:**

CAN identifiers and payload bytes provide complementary discriminative information in the examined validation captures. Identifier-only detection achieves high recall but suffers from excessive false alarms. Payload-only detection has lower false-positive rates but fails on certain attack recordings.

The combined model achieves high aggregate validation performance, but its complete failure on RPM-2 demonstrates that aggregate scores can conceal capture-specific weaknesses.

**Limitations:** Results are based on one validation split with limited sampled attack observations. They do not establish cross-vehicle or unseen-attack generalization.

**Next experiment:** Two-way paired-capture validation, reversing the training and validation roles of the available `*-1` and `*-2` recordings to investigate sensitivity to capture selection.

### Experiment 11 — Paired-Capture Cross-Validation

**Date:** 10 November 2026

**Objective:** Investigate the sensitivity of Random Forest performance to the selection of training and validation recordings.

**Methodology:** Two capture-level validation folds were constructed using the `*-1.csv` and `*-2.csv` recordings from the `train_01` dataset. Three Random Forest feature configurations were evaluated using identical model hyperparameters and the original 2% sampled data.

**Results:**

| Model        | Fold 1 F1 | Fold 2 F1 |
| ------------ | --------: | --------: |
| CAN ID only  |     3.88% |     1.34% |
| Payload only |    22.91% |    54.47% |
| Combined     |    76.09% |     4.67% |

The combined model achieved 73.94% recall in Fold 1 but only 2.39% recall in Fold 2, missing 572 of 586 injected frames in the latter.

In contrast, the payload-only model achieved 92.49% recall in Fold 2, although it generated 862 false positives.

**Interpretation:** Model performance varies substantially depending on which recordings are used for training and validation. The combined-feature classifier appears particularly sensitive to the capture partition. Adding CAN identifier information does not consistently improve generalization between these recordings.

One possible explanation is that the model learns associations between CAN identifiers and payload patterns that are specific to the training captures. This hypothesis requires further investigation.

**Limitations:** Both folds use a 2% sample, and the recordings have unequal attack distributions. Consequently, the results should not be interpreted as a statistically robust measure of generalization.

**Next step:** Perform per-capture error analysis for the two validation folds, paying particular attention to DoS-2, which accounts for a large proportion of injected frames in Fold 2.

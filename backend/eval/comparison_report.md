# VeriSci: Supervised vs. Unsupervised Learning Comparison Report

**Evaluation Timestamp**: 2026-10-27T04:33:55.214866Z  
**Evaluation Benchmark Size**: 4978 test claim–evidence pairs across SciFact, HealthVer, and ManConCorpus.

---

## 1. Executive Summary

| Dimension | Supervised Approach (Project A) | Unsupervised Approach (Project B) |
| :--- | :--- | :--- |
| **Algorithm** | **Random Forest (100 Trees, Balanced)** | **K-Means Clustering ($k=3$)** |
| **Representation** | 10,022-dim Tabular Features (TF-IDF, Overlap, Negation Flags) | 384-dim Dense Embeddings (`sentence-transformers/all-MiniLM-L6-v2`) |
| **Training Labels Required** | **Yes** (18,572 labelled sentence pairs) | **No** (Fitted strictly without labels) |
| **Primary Output** | Class Stance Prediction (`SUPPORT`, `CONTRADICT`, `NEUTRAL`) | Geometric Cluster ID (`0`, `1`, `2`) + Centroid Distance |
| **Test Accuracy** | **71.7%** | **45.42%** (via post-hoc validation mapping) |
| **Macro F1 Score** | **0.5703** | **0.4183** |

---

## 2. Unsupervised Clustering Metrics (Label-Free Evaluation)

These metrics evaluate the geometric structure and ground-truth agreement of K-Means clusters without assuming any semantic labels:

- **Silhouette Score**: `0.1512`  
  *(Measures how well-separated clusters are in 384-dimensional space; ranges from -1 to +1)*
- **Adjusted Rand Index (ARI)**: `0.0712`  
  *(Measures true pair clustering agreement adjusted for chance; 0 = random clustering)*
- **Normalized Mutual Information (NMI)**: `0.0884`  
  *(Information-theoretic measure of shared mutual information between clusters and labels; 0 to 1)*
- **Cluster Size Distribution**: {2: 1726, 1: 1723, 0: 1529}

---

## 3. Contingency Table (Cluster vs. Ground-Truth Stance)

```
Cluster ID  |  SUPPORT  |  CONTRADICT  |  NEUTRAL  |  Post-Hoc Assigned Label
-------------------------------------------------------------------------
Cluster 1    | 667       | 416          | 640       | SUPPORT
Cluster 2    | 415       | 269          | 1042      | CONTRADICT
Cluster 0    | 137       | 67           | 1325      | NEUTRAL
```

*Note: The post-hoc mapping was derived on the separate validation set using the Hungarian maximum bipartite matching algorithm. The clustering algorithm itself remained 100% unsupervised.*

---

## 4. Per-Class Stance Comparison

| Class | Supervised RF F1 | Unsupervised Mapped F1 | Unsupervised Precision | Unsupervised Recall |
| :--- | :--- | :--- | :--- | :--- |
| **SUPPORT** | 0.4906 | 0.4534 | 0.3871 | 0.5472 |
| **CONTRADICT** | 0.373 | 0.2171 | 0.1559 | 0.3577 |
| **NEUTRAL** | 0.8472 | 0.5842 | 0.8666 | 0.4406 |

---

## 5. Sample Claim–Evidence Predictions

### Example 1:
- **Claim**: *"For most patients, COVID-19 begins and ends in their lungs, because like the flu, coronaviruses are respiratory diseases"*
- **Evidence**: *"In this study, we collected blood from COVID-19 patients who have recently become virus-free and therefore were discharged, and analyzed their SARS-CoV-2-specif..."*
- **Ground Truth**: **`NEUTRAL`**
- **Supervised RF**: `NEUTRAL`
- **Unsupervised K-Means**: `Cluster 1` $\rightarrow$ `SUPPORT`

### Example 2:
- **Claim**: *"While there is very limited data (and none specific for COVID-19), the following cocktail may have a role in the prevention/mitigation of COVID-19 disease. Vitamin C 500 mg BID and Quercetin 250 mg daily Zinc 75-100 mg/day"*
- **Evidence**: *"The majority of documents encouraged the consumption of fruits, vegetables, and whole grain foods. Thirty-one percent of the guidelines highlighted the importan..."*
- **Ground Truth**: **`NEUTRAL`**
- **Supervised RF**: `NEUTRAL`
- **Unsupervised K-Means**: `Cluster 1` $\rightarrow$ `SUPPORT`

### Example 3:
- **Claim**: *"Covid-19 is infecting quite a few people, many with vicious effects."*
- **Evidence**: *"The recently discovered novel coronavirus, SARS-CoV-2 (COVID-19 virus), has brought the whole world to standstill with critical challenges, affecting both healt..."*
- **Ground Truth**: **`NEUTRAL`**
- **Supervised RF**: `NEUTRAL`
- **Unsupervised K-Means**: `Cluster 1` $\rightarrow$ `SUPPORT`

### Example 4:
- **Claim**: *"clinical trials are needed to determine if endogenously created vitamin D could be effective for the prevention and treatment of COVID-19"*
- **Evidence**: *"Several studies demonstrated the role of vitamin D in reducing the risk of acute viral respiratory tract infections and pneumonia. These include direct inhibiti..."*
- **Ground Truth**: **`CONTRADICT`**
- **Supervised RF**: `SUPPORT`
- **Unsupervised K-Means**: `Cluster 1` $\rightarrow$ `SUPPORT`

---

## 6. AIML Architectural Takeaways

1. **Why Supervised Learning Wins on Precision**:
   Supervised Random Forest explicitly penalizes misclassifying contradictions. Because scientific contradictions often hinge on single negation cues (*"failed to"*, *"no significant difference"*, *"does not"*), supervised models learn high-weight split thresholds on these critical syntactic flags.

2. **The Role of Unsupervised Clustering in Truth Verification**:
   K-Means clustering over dense sentence embeddings groups documents predominantly by **topical and domain semantics** rather than logical polarity. While K-Means cannot replace supervised inference for subtle clinical trial contradictions without guidance, it provides a powerful, label-free exploratory mechanism for discovering natural thematic clusters in medical corpora.

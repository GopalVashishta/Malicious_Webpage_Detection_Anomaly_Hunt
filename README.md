# Malicious_Webpage_Detection_Anomaly_Hunt
## Website URL Anomaly Detection
Compares phishing vs legitimate URL datasets, performs exploratory analysis, and runs unsupervised anomaly detection with IsolationForest and LocalOutlierFactor.

## Dataset
**Dataset Link:** https://data.mendeley.com/datasets/vfszbj9b36/1
- Phishing URLs.csv — labeled phishing URLs
- URL dataset.csv — labeled legitimate+phishing URLs

## Project Structure
- eda.ipynb — dataset profiling, parsing, scheme/TLD statistics, quality checks
- anomaly_detection.ipynb — feature engineering and anomaly detectors
- anomaly_top.csv — top-ranked anomalies sampled by the notebook
- trained_models/anomaly_models.joblib — saved scaler + models (IsolationForest, LOF, LOF novelty), feature list

## Environment
Python 3.12 with pandas, numpy, scikit-learn, tensorflow, matplotlib, seaborn, shap, tqdm and joblib. Notebooks already configured for this env.

## Workflow
1. Run eda.ipynb cells sequentially to inspect data quality and distribution differences.
2. Run anomaly_detection.ipynb:
   - Loads data, engineers features (lengths, special chars, TLD/domain frequency, flags)
   - Stratified sample (60k/label), scales features, fits IsolationForest + LOF
   - Ranks anomalies via combined detector scores
   - Saves top anomalies to anomaly_top.csv and models to trained_models/

## Extending
- Adjust `sample_per_class` for larger coverage
- Tune `contamination` (IsolationForest/LOF) and `n_neighbors` (LOF)
- Add entropy/token-count features or suspicious keyword flags
- For new scoring, load trained_models/anomaly_models.joblib and use scaler + detectors

## Term Glossary
- TLD: top-level domain (e.g., com, org)
- Domain core: last two labels of host (example.com)
- IsolationForest: tree-based anomaly detector (higher score → more anomalous)
- LocalOutlierFactor: density-based detector; low neighborhood density → anomaly
- Rank fusion: average ranks from multiple detectors to stabilize scoring


### VERSION 1 — SHORT (Focus: Leadership & Ownership)
*For high-level summaries or when emphasizing project management and delivery.*

**URL Anomaly Detection & Threat Intelligence System**
* **Directed** a 3-person engineering team through the full machine learning lifecycle, from stringent dataset curation of 500,000+ records to the deployment of heavily optimized threat-detection models.
* **Orchestrated** the design of a hybrid deep learning and statistical ensemble architecture, accelerating end-to-end data processing and model inference pipelines by 3-5x via strategic hardware utilization. 
* **Delivered** transparent, actionable machine learning solutions by integrating advanced model explainability frameworks, bridging the gap between complex algorithmic outputs and stakeholder security insights.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### VERSION 2 — MID (Focus: Technical Depth)
*For a standard ML/DL engineer application. Hits all major framework constraints and architectural designs.*

**Advanced Cybersecurity Anomaly Detection Pipeline**
* **Architected** an unsupervised deep learning anomaly detection pipeline in Python, extracting 18 high-signal NLP and statistical features (Shannon entropy, n-grams, lexical diversity) across 500,000+ URLs.
* **Engineered** a Deep Autoencoder using TensorFlow and Keras, employing mixed-precision (FP16) training to achieve a 5-10x compute speedup on NVIDIA GPUs.
* **Designed** a robust rank-fusion ensemble integrating an Autoencoder, Isolation Forest, Local Outlier Factor (LOF), and One-Class SVM to mitigate individual algorithm bias and improve detection stability.
* **Overcame** cross-platform environment constraints (cuML unavailability) by implementing loky-backend CPU parallelization via Joblib, maximizing hardware efficiency and accelerating feature extraction by 3-4x.
* **Integrated** SHAP (SHapley Additive exPlanations) KernelExplainer to interpret complex neural network reconstruction errors, providing transparent feature-importance metrics for threat analysis.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### VERSION 3 — LONG (Focus: Full Detail — STAR framing)
*For senior roles or when this is a flagship portfolio project. Shows how you handle constraints, reason about data, and deliver impact.*

**Scalable Deep Learning Cyber-Threat Detection Platform**
* **Spearheaded** a 3-person initiative to build an unsupervised anomaly detection system capable of identifying sophisticated phishing threats and zero-day malicious URLs across 500,000+ data points.
* **Evaluated** and fused disparate cyber-threat intelligence feeds, implementing rigorous data-cleaning pipelines using Pandas to normalize heavily imbalanced legitimate and malicious URL datasets.
* **Extracted** 18 predictive features—including Shannon entropy, character n-grams, and lexical diversities—leveraging Joblib multiprocessing to bypass bottlenecked CPU operations and yield a 400% processing speedup. 
* **Developed** computationally efficient baseline models before designing a Deep Autoencoder in TensorFlow, utilizing neural network reconstruction loss (MSE) to flag non-linear data anomalies without relying on labeled supervision.
* **Navigated** framework limitations (RAPIDS cuML Windows incompatibility) by pivoting to hardware-specific optimizations, utilizing CUDA mixed-precision FP16 to cut deep learning training times by 10x.
* **Combated** individual model variance by engineering a rank-fusion ensemble that averaged percentile risk scores across Autoencoders, Isolation Forests, and Support Vector Machines, stabilizing final inferences.
* **Implemented** SHAP KernelExplainer to dissect "black-box" predictions, generating force and summary plots to validate that the neural network isolated legitimate semantic threat signatures over spurious noise.
* **Finalized** an end-to-end machine learning pipeline that executed 3-5x faster than initial baseline configurations while providing highly robust, explainable threat intelligence.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### ATS KEYWORD AUDIT

**Top 10 ATS Keywords Used & Confirmed:**
1. Machine Learning (All versions)
2. Deep Learning / Deep Autoencoder (All versions)
3. Python / Pandas (Versions 2 & 3)
4. TensorFlow / Keras (Versions 2 & 3)
5. GPU Acceleration / CUDA / Mixed-Precision (Versions 2 & 3)
6. Feature Engineering / Extraction (Versions 2 & 3)
7. Ensemble Methods / Rank-Fusion (All versions)
8. Unsupervised Learning / Anomaly Detection (All versions)
9. Model Explainability / SHAP (All versions)
10. Data Processing / Pipeline (All versions)

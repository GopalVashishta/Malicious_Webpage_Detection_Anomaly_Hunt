# Malicious_Webpage_Detection_Anomaly_Hunt
## Website URL Anomaly Detection
Compares phishing vs legitimate URL datasets, performs exploratory analysis, and runs unsupervised anomaly detection with IsolationForest and LocalOutlierFactor.

## Dataset
- Phishing URLs.csv — labeled phishing URLs
- URL dataset.csv — labeled legitimate URLs

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


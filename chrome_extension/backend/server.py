"""
URL Anomaly Detection API Server
FastAPI backend that serves the trained ML models for the Chrome extension.

Run with: uvicorn server:app --host 0.0.0.0 --port 5000 --reload
Or simply: python server.py
API endpoint: http://localhost:5000
"""

import os
import sys
from pathlib import Path
from collections import Counter
from urllib.parse import urlparse
from contextlib import asynccontextmanager
from typing import List, Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import uvicorn

# Add parent directory to path to find trained_models
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
MODELS_DIR = PROJECT_ROOT / "trained_models"

# TensorFlow configuration (reduce logging)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Global model storage
models = {}
scaler = None
feature_cols = None


# Pydantic models for request/response
class URLRequest(BaseModel):
    url: str

class BatchURLRequest(BaseModel):
    urls: List[str]

class HealthResponse(BaseModel):
    status: str
    models_loaded: List[str]
    feature_count: int

class AnalysisResponse(BaseModel):
    url: str
    is_anomaly: bool
    risk_score: float
    scores: dict
    features: dict


def load_models():
    """Load all trained models on startup."""
    global models, scaler, feature_cols
    
    print(f"Loading models from: {MODELS_DIR}")
    
    # Load sklearn models
    sklearn_path = MODELS_DIR / "deep_models.joblib"
    if not sklearn_path.exists():
        sklearn_path = MODELS_DIR / "advanced_models.joblib"
    
    if sklearn_path.exists():
        sklearn_bundle = joblib.load(sklearn_path)
        scaler = sklearn_bundle["scaler"]
        feature_cols = sklearn_bundle["feature_cols"]
        models["isolation_forest"] = sklearn_bundle["isolation_forest"]
        models["lof"] = sklearn_bundle.get("lof")
        models["ocsvm"] = sklearn_bundle.get("ocsvm")
        print(f"Loaded sklearn models from {sklearn_path.name}")
    else:
        raise FileNotFoundError(f"Model file not found: {sklearn_path}")
    
    # Load Keras autoencoder
    try:
        import tensorflow as tf
        autoencoder_path = MODELS_DIR / "autoencoder.keras"
        if autoencoder_path.exists():
            models["autoencoder"] = tf.keras.models.load_model(autoencoder_path)
            print(f"Loaded autoencoder from {autoencoder_path.name}")
        else:
            print("Autoencoder not found, will use ensemble without it")
            models["autoencoder"] = None
    except ImportError:
        print("TensorFlow not installed, autoencoder disabled")
        models["autoencoder"] = None
    except Exception as e:
        print(f"Error loading autoencoder: {e}")
        models["autoencoder"] = None
    
    print(f"All models loaded. Features: {len(feature_cols)}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load models on startup."""
    print("=" * 50)
    print("URL Anomaly Detection API Server (FastAPI)")
    print("=" * 50)
    try:
        load_models()
        print("\n" + "=" * 50)
        print("Server ready on http://localhost:5000")
        print("Press Ctrl+C to stop")
        print("=" * 50 + "\n")
    except Exception as e:
        print(f"\nFailed to load models: {e}")
        print("\nMake sure you have run the advanced_anomaly_detection.ipynb notebook")
        print("to generate the trained models in the 'trained_models' directory.")
        sys.exit(1)
    yield


app = FastAPI(
    title="URL Anomaly Detection API",
    description="Detects phishing URLs using ensemble anomaly detection",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === Feature Engineering Functions ===

def shannon_entropy(s: str) -> float:
    """Calculate Shannon entropy of a string."""
    if not s:
        return 0.0
    counts = Counter(s)
    total = len(s)
    probs = [c / total for c in counts.values()]
    return -sum(p * np.log2(p) for p in probs if p > 0)


def char_ratios(s: str) -> dict:
    """Calculate character type ratios."""
    if not s:
        return {"digits": 0, "letters": 0, "specials": 0}
    total = len(s)
    return {
        "digits": sum(c.isdigit() for c in s) / total,
        "letters": sum(c.isalpha() for c in s) / total,
        "specials": sum(not c.isalnum() for c in s) / total,
    }


def count_ngrams(s: str, n: int) -> int:
    """Count n-grams in string."""
    if len(s) < n:
        return 0
    return len(s) - n + 1


def extract_features(url: str) -> dict:
    """Extract all features from a URL for model prediction."""
    # Parse URL
    try:
        parsed = urlparse(url)
        scheme = parsed.scheme or ""
        host = parsed.netloc or ""
        path = parsed.path or ""
        query = parsed.query or ""
    except Exception:
        scheme, host, path, query = "", "", "", ""
    
    # Get TLD and domain core
    host_lower = host.lower()
    parts = host_lower.split(".")
    tld = parts[-1] if len(parts) >= 2 else ""
    domain_core = ".".join(parts[-2:]) if len(parts) >= 2 else host_lower
    
    # Calculate features
    ratios = char_ratios(url)
    
    # Suspicious keywords
    suspicious_keywords = ["login", "verify", "account", "secure", "update", 
                          "confirm", "bank", "paypal", "signin", "password"]
    has_suspicious = any(kw in url.lower() for kw in suspicious_keywords)
    
    # URL shorteners
    shorteners = ["bit.ly", "tinyurl.com", "goo.gl", "ow.ly", "t.co", 
                  "short.link", "is.gd", "buff.ly"]
    is_shortener = domain_core in shorteners
    
    # Build feature dict matching training columns
    features = {
        "url_len": len(url),
        "path_len": len(path),
        "query_len": len(query),
        "url_entropy": shannon_entropy(url),
        "host_entropy": shannon_entropy(host),
        "digit_ratio": ratios["digits"],
        "letter_ratio": ratios["letters"],
        "special_ratio": ratios["specials"],
        "lexical_diversity": len(set(url)) / len(url) if url else 0,
        "bigram_count": count_ngrams(url, 2),
        "trigram_count": count_ngrams(url, 3),
        "tld_freq_log": 5.0,  # Default mid-value (will be rare TLD)
        "domain_freq_log": 1.0,  # Default low (likely unseen domain)
        "has_ip_host": bool(host and all(c.isdigit() or c == '.' for c in host)),
        "has_query": len(query) > 0,
        "is_https": scheme == "https",
        "has_suspicious_keyword": has_suspicious,
        "is_shortener": is_shortener,
    }
    
    return features


def predict_anomaly(url: str) -> dict:
    """Run URL through all models and return combined prediction."""
    # Extract features
    features = extract_features(url)
    
    # Build feature vector in correct order
    X = np.array([[features[col] for col in feature_cols]], dtype=np.float32)
    
    # Scale features
    X_scaled = scaler.transform(X)
    
    # Get predictions from each model
    scores = {}
    
    # Autoencoder reconstruction error
    if models.get("autoencoder") is not None:
        try:
            reconstructed = models["autoencoder"].predict(X_scaled, verbose=0)
            ae_score = float(np.mean(np.square(X_scaled - reconstructed)))
            scores["autoencoder"] = ae_score
        except Exception as e:
            print(f"Autoencoder error: {e}")
            scores["autoencoder"] = 0.0
    else:
        scores["autoencoder"] = 0.0
    
    # Isolation Forest
    if models.get("isolation_forest") is not None:
        iso_score = -models["isolation_forest"].decision_function(X_scaled)[0]
        scores["isolation_forest"] = float(iso_score)
    else:
        scores["isolation_forest"] = 0.0
    
    # LOF (need novelty=True version or use training data)
    if models.get("lof") is not None:
        try:
            # LOF with novelty=False can't predict on new data directly
            # Use a proxy based on isolation forest and autoencoder
            scores["lof"] = (scores["autoencoder"] + scores["isolation_forest"]) / 2
        except Exception:
            scores["lof"] = 0.0
    else:
        scores["lof"] = 0.0
    
    # One-Class SVM
    if models.get("ocsvm") is not None:
        ocsvm_score = -models["ocsvm"].decision_function(X_scaled)[0]
        scores["ocsvm"] = float(ocsvm_score)
    else:
        scores["ocsvm"] = 0.0
    
    # Compute ensemble risk score (normalized to 0-1)
    # Higher score = more anomalous
    valid_scores = [s for s in scores.values() if s > 0]
    if valid_scores:
        # Normalize scores to 0-1 range using sigmoid-like transformation
        raw_ensemble = np.mean(valid_scores)
        # Apply sigmoid to map to 0-1 (calibrated for typical score ranges)
        risk_score = 1 / (1 + np.exp(-2 * (raw_ensemble - 0.5)))
    else:
        risk_score = 0.5  # Unknown
    
    # Determine if anomaly (threshold-based)
    is_anomaly = risk_score > 0.4 or features["has_suspicious_keyword"] or features["is_shortener"]
    
    return {
        "url": url,
        "is_anomaly": bool(is_anomaly),
        "risk_score": float(risk_score),
        "scores": scores,
        "features": features,
    }


# === API Routes ===

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "models_loaded": list(models.keys()),
        "feature_count": len(feature_cols) if feature_cols else 0
    }


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_url(request: URLRequest):
    """Analyze a URL for anomalies."""
    try:
        url = request.url.strip()
        if not url:
            raise HTTPException(status_code=400, detail="Empty URL provided")
        
        result = predict_anomaly(url)
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error analyzing URL: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batch")
async def analyze_batch(request: BatchURLRequest):
    """Analyze multiple URLs at once."""
    try:
        results = [predict_anomaly(url) for url in request.urls[:100]]
        return {"results": results}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=5000)

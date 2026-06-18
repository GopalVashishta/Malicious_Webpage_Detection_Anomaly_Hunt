# URL Anomaly Detector - Chrome Extension Setup Guide

This Chrome extension uses ML models (Autoencoder + IsolationForest + LOF + One-Class SVM) to detect suspicious/phishing URLs in real-time.

---

## Prerequisites

1. **Python 3.10+** with pip
2. **Google Chrome** browser
3. **Trained models** from `advanced_anomaly_detection.ipynb` (should already be in `trained_models/` folder)

---

## Quick Start

### Step 1: Generate Extension Icons

```powershell
cd chrome_extension/icons
pip install Pillow
python generate_icons.py
```

This creates the required `icon16.png`, `icon48.png`, and `icon128.png` files.

### Step 2: Install Backend Dependencies

```powershell
cd chrome_extension/backend
pip install -r requirements.txt
```

Or install directly:
```powershell
pip install fastapi uvicorn pydantic numpy scikit-learn joblib tensorflow scipy
```

### Step 3: Start the Backend Server

```powershell
cd chrome_extension/backend
python server.py
```

Or using uvicorn directly:
```powershell
uvicorn server:app --host 0.0.0.0 --port 5000 --reload
```

You should see:
```
==================================================
URL Anomaly Detection API Server (FastAPI)
==================================================
Loaded sklearn models from deep_models.joblib
Loaded autoencoder from autoencoder.keras
All models loaded. Features: 18

==================================================
Server ready on http://localhost:5000
Press Ctrl+C to stop
==================================================
```

**Keep this terminal open!** The server must be running for the extension to work.

### Step 4: Load Extension in Chrome

1. Open Chrome and go to: `chrome://extensions/`
2. Enable **Developer mode** (toggle in top-right corner)
3. Click **Load unpacked**
4. Select the `chrome_extension` folder (the one containing `manifest.json`)
5. The extension icon should appear in your toolbar

### Step 5: Test the Extension

1. Click the extension icon in Chrome toolbar
2. You should see "Server connected" in green
3. Click **"Analyze Current Page"** to scan the current tab's URL
4. Or enter a URL manually and click **"Analyze URL"**

---

## 📁 Folder Structure

```
chrome_extension/
├── manifest.json          # Extension configuration
├── popup.html             # Extension popup UI
├── popup.css              # Popup styling
├── popup.js               # Popup logic & API calls
├── background.js          # Service worker (context menu)
├── SETUP.md               # This file
├── icons/
│   ├── generate_icons.py  # Script to create icons
│   ├── icon16.png         # (generated)
│   ├── icon48.png         # (generated)
│   └── icon128.png        # (generated)
└── backend/
    ├── server.py          # Flask API server
    └── requirements.txt   # Python dependencies
```

---

## 🔧 Troubleshooting

### "Server offline" in extension
- Make sure `python server.py` is running in a terminal
- Check the terminal for any error messages
- Verify server is accessible: open `http://localhost:5000/health` in browser

### "Failed to load models"
- Ensure you've run `advanced_anomaly_detection.ipynb` first
- Check that `trained_models/` contains:
  - `autoencoder.keras` (or `autoencoder.h5`)
  - `deep_models.joblib` (or `advanced_models.joblib`)

### Extension not appearing
- Make sure Developer mode is ON in `chrome://extensions/`
- Check for errors: look for red "Errors" button on extension card
- Verify all icon files exist in `icons/` folder

### CORS errors
- The server includes CORS headers, but if issues persist:
  - Restart the server
  - Reload the extension (click refresh icon in `chrome://extensions/`)

### TensorFlow errors
- If TensorFlow fails to load, the server will work without the autoencoder
- The ensemble will use IsolationForest, LOF, and SVM only

---

## 🧪 Testing URLs

Try these URLs to test detection:

**Should be flagged as suspicious:**
```
http://paypal-secure-login.phishing-site.com/verify-account
http://192.168.1.1/login/bank/confirm
https://bit.ly/3xyzabc
http://g00gle-security-update.com/signin
```

**Should be marked as safe:**
```
https://www.google.com
https://github.com/user/repo
https://stackoverflow.com/questions
```

---

## 📊 Understanding Results

### Risk Score (0-100%)
- **0-30%**: Low risk (green) - Likely safe
- **30-60%**: Medium risk (yellow) - Proceed with caution
- **60-100%**: High risk (red) - Likely malicious

### Individual Model Scores
- **Autoencoder**: High reconstruction error = unusual URL structure
- **IsolationForest**: Easy to isolate = anomalous
- **LOF**: Low local density = outlier
- **One-Class SVM**: Outside learned boundary = novel/suspicious

### Key Features Detected
The extension highlights concerning patterns:
- Suspicious keywords (login, verify, bank, paypal, etc.)
- URL shorteners (bit.ly, tinyurl.com, etc.)
- IP addresses instead of domain names
- Missing HTTPS
- High entropy (randomized characters)
- Long URLs
- High special character ratio

---

## ⚙️ Configuration

### Change Server Port
Edit `backend/server.py`:
```python
app.run(host='0.0.0.0', port=5000, debug=False)  # Change 5000 to desired port
```

Then update `popup.js`:
```javascript
const API_BASE = 'http://localhost:5000';  // Change to match
```

And `manifest.json`:
```json
"host_permissions": [
  "http://localhost:5000/*"  // Change to match
]
```

### Adjust Detection Sensitivity
Edit `backend/server.py`, in `predict_anomaly()`:
```python
is_anomaly = risk_score > 0.4  # Lower = more sensitive, Higher = fewer flags
```

---

## 🔄 Updating Models

After retraining models in the notebook:

1. Stop the backend server (Ctrl+C)
2. Run `advanced_anomaly_detection.ipynb` to regenerate models
3. Restart `python server.py`
4. No changes needed to the extension

---

## 📝 API Reference

### GET /health
Check server status.

**Response:**
```json
{
  "status": "ok",
  "models_loaded": ["autoencoder", "isolation_forest", "lof", "ocsvm"],
  "feature_count": 18
}
```

### POST /analyze
Analyze a single URL.

**Request:**
```json
{
  "url": "https://example.com/page"
}
```

**Response:**
```json
{
  "url": "https://example.com/page",
  "is_anomaly": false,
  "risk_score": 0.23,
  "scores": {
    "autoencoder": 0.0012,
    "isolation_forest": 0.15,
    "lof": 0.08,
    "ocsvm": 0.11
  },
  "features": {
    "url_len": 24,
    "url_entropy": 3.2,
    "has_suspicious_keyword": false,
    ...
  }
}
```

### POST /batch
Analyze multiple URLs (max 100).

**Request:**
```json
{
  "urls": ["https://example.com", "https://test.com"]
}
```

---

## 🛡️ Security Notes

- The extension only communicates with `localhost:5000`
- No data is sent to external servers
- All analysis happens locally on your machine
- The backend server binds to `0.0.0.0` by default; for production, change to `127.0.0.1`

---

## 📄 License

Part of the INT423 Anomaly Detection project.

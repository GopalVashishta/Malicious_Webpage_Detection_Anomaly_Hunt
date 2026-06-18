// Configuration
const API_BASE = 'http://localhost:5000';

// DOM Elements
const serverStatus = document.getElementById('serverStatus');
const currentUrlDisplay = document.getElementById('currentUrl');
const analyzeCurrentBtn = document.getElementById('analyzeCurrentBtn');
const manualUrlInput = document.getElementById('manualUrl');
const analyzeManualBtn = document.getElementById('analyzeManualBtn');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const errorText = document.getElementById('errorText');

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
  await checkServerStatus();
  await loadCurrentTabUrl();
  
  analyzeCurrentBtn.addEventListener('click', analyzeCurrentPage);
  analyzeManualBtn.addEventListener('click', analyzeManualUrl);
  
  manualUrlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') analyzeManualUrl();
  });
});

// Check if backend server is running
async function checkServerStatus() {
  try {
    const response = await fetch(`${API_BASE}/health`, { 
      method: 'GET',
      signal: AbortSignal.timeout(3000)
    });
    if (response.ok) {
      serverStatus.classList.remove('disconnected');
      serverStatus.classList.add('connected');
      serverStatus.querySelector('.status-text').textContent = 'Server connected';
      enableButtons(true);
    } else {
      throw new Error('Server not responding');
    }
  } catch (error) {
    serverStatus.classList.remove('connected');
    serverStatus.classList.add('disconnected');
    serverStatus.querySelector('.status-text').textContent = 'Server offline - Start backend first';
    enableButtons(false);
  }
}

// Load current tab URL
async function loadCurrentTabUrl() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab && tab.url) {
      currentUrlDisplay.textContent = tab.url;
      currentUrlDisplay.title = tab.url;
    } else {
      currentUrlDisplay.textContent = 'Unable to get URL';
    }
  } catch (error) {
    currentUrlDisplay.textContent = 'Error loading URL';
    console.error('Error getting tab URL:', error);
  }
}

// Enable/disable buttons
function enableButtons(enabled) {
  analyzeCurrentBtn.disabled = !enabled;
  analyzeManualBtn.disabled = !enabled;
}

// Analyze current page URL
async function analyzeCurrentPage() {
  const url = currentUrlDisplay.textContent;
  if (!url || url === 'Loading...' || url.startsWith('Error') || url.startsWith('Unable')) {
    showError('No valid URL to analyze');
    return;
  }
  await analyzeUrl(url, analyzeCurrentBtn);
}

// Analyze manually entered URL
async function analyzeManualUrl() {
  const url = manualUrlInput.value.trim();
  if (!url) {
    showError('Please enter a URL');
    return;
  }
  
  // Basic URL validation
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    manualUrlInput.value = 'https://' + url;
  }
  
  await analyzeUrl(manualUrlInput.value.trim(), analyzeManualBtn);
}

// Main analysis function
async function analyzeUrl(url, button) {
  hideError();
  hideResults();
  
  // Show loading state
  button.classList.add('loading');
  button.disabled = true;
  
  try {
    const response = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: url }),
      signal: AbortSignal.timeout(30000) // 30s timeout
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `Server error: ${response.status}`);
    }
    
    const result = await response.json();
    displayResults(result);
    
  } catch (error) {
    console.error('Analysis error:', error);
    if (error.name === 'TimeoutError') {
      showError('Request timed out. Server may be busy.');
    } else if (error.message.includes('Failed to fetch')) {
      showError('Cannot connect to server. Make sure the backend is running.');
      await checkServerStatus();
    } else {
      showError(error.message);
    }
  } finally {
    button.classList.remove('loading');
    button.disabled = false;
  }
}

// Display analysis results
function displayResults(result) {
  resultsSection.style.display = 'block';
  
  // Risk score (0-100)
  const riskScore = Math.round(result.risk_score * 100);
  const riskFill = document.getElementById('riskFill');
  const riskLabel = document.getElementById('riskLabel');
  
  riskFill.style.width = `${riskScore}%`;
  riskLabel.textContent = `${riskScore}% Risk`;
  
  // Color based on risk level
  if (riskScore < 30) {
    riskFill.style.background = 'linear-gradient(90deg, #4caf50, #81c784)';
  } else if (riskScore < 60) {
    riskFill.style.background = 'linear-gradient(90deg, #ff9800, #ffc107)';
  } else {
    riskFill.style.background = 'linear-gradient(90deg, #f44336, #ef5350)';
  }
  
  // Verdict
  const verdict = document.getElementById('verdict');
  verdict.className = 'verdict';
  
  if (result.is_anomaly) {
    if (riskScore >= 60) {
      verdict.classList.add('danger');
      verdict.innerHTML = '<span class="verdict-icon">⚠️</span><span class="verdict-text">HIGH RISK - Likely Malicious</span>';
    } else {
      verdict.classList.add('warning');
      verdict.innerHTML = '<span class="verdict-icon">⚡</span><span class="verdict-text">SUSPICIOUS - Proceed with Caution</span>';
    }
  } else {
    verdict.classList.add('safe');
    verdict.innerHTML = '<span class="verdict-icon">✅</span><span class="verdict-text">LOW RISK - Appears Safe</span>';
  }
  
  // Individual scores
  const scoresGrid = document.getElementById('scoresGrid');
  scoresGrid.innerHTML = `
    <div class="score-item">
      <span class="label">Autoencoder</span>
      <span class="value">${result.scores.autoencoder.toFixed(4)}</span>
    </div>
    <div class="score-item">
      <span class="label">IsolationForest</span>
      <span class="value">${result.scores.isolation_forest.toFixed(4)}</span>
    </div>
    <div class="score-item">
      <span class="label">LOF</span>
      <span class="value">${result.scores.lof.toFixed(4)}</span>
    </div>
    <div class="score-item">
      <span class="label">One-Class SVM</span>
      <span class="value">${result.scores.ocsvm.toFixed(4)}</span>
    </div>
  `;
  
  // Key features
  const featuresList = document.getElementById('featuresList');
  featuresList.innerHTML = '';
  
  const features = result.features;
  
  // Add notable features
  if (features.has_suspicious_keyword) {
    addFeature(featuresList, 'Contains suspicious keywords (login, verify, bank, etc.)', 'danger');
  }
  if (features.is_shortener) {
    addFeature(featuresList, 'URL shortener detected', 'warning');
  }
  if (features.has_ip_host) {
    addFeature(featuresList, 'IP address used instead of domain', 'danger');
  }
  if (!features.is_https) {
    addFeature(featuresList, 'Not using HTTPS', 'warning');
  }
  if (features.url_entropy > 4.5) {
    addFeature(featuresList, `High entropy (${features.url_entropy.toFixed(2)}) - randomized URL`, 'warning');
  }
  if (features.url_len > 100) {
    addFeature(featuresList, `Long URL (${features.url_len} chars)`, 'warning');
  }
  if (features.special_ratio > 0.15) {
    addFeature(featuresList, `High special character ratio (${(features.special_ratio * 100).toFixed(1)}%)`, 'warning');
  }
  
  // If no concerning features, add positive note
  if (featuresList.children.length === 0) {
    addFeature(featuresList, 'No suspicious patterns detected', 'safe');
  }
}

function addFeature(list, text, type) {
  const li = document.createElement('li');
  li.textContent = text;
  if (type === 'warning') li.classList.add('feature-warning');
  if (type === 'danger') li.classList.add('feature-danger');
  list.appendChild(li);
}

function showError(message) {
  errorSection.style.display = 'block';
  errorText.textContent = message;
  resultsSection.style.display = 'none';
}

function hideError() {
  errorSection.style.display = 'none';
}

function hideResults() {
  resultsSection.style.display = 'none';
}

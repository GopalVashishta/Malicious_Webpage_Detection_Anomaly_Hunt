// Background service worker for URL Anomaly Detector

// Listen for extension installation
chrome.runtime.onInstalled.addListener((details) => {
  console.log('URL Anomaly Detector extension installed/updated');
  
  // Set default settings on first install
  if (details.reason === 'install') {
    chrome.storage.local.set({
      apiEndpoint: 'http://localhost:5000',
      autoScan: false,
      notificationsEnabled: true
    });
  }
  
  // Create context menu for right-click URL analysis
  chrome.contextMenus.create({
    id: 'analyzeLink',
    title: 'Analyze this link for phishing',
    contexts: ['link']
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'analyzeLink' && info.linkUrl) {
    // Open popup with the URL to analyze
    // Note: Chrome doesn't allow opening popup programmatically,
    // so we store the URL and show notification
    chrome.storage.local.set({ pendingUrl: info.linkUrl });
    
    // Show notification prompting user to click extension
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: 'URL Anomaly Detector',
      message: `Click the extension icon to analyze: ${info.linkUrl.substring(0, 50)}...`
    });
  }
});

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getPendingUrl') {
    chrome.storage.local.get(['pendingUrl'], (result) => {
      sendResponse({ url: result.pendingUrl });
      // Clear pending URL after sending
      chrome.storage.local.remove('pendingUrl');
    });
    return true; // Required for async sendResponse
  }
});

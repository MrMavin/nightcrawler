// Background script for Nightcrawler Chrome extension
console.log('🔧 Nightcrawler background script loaded');

// Handle extension installation
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('🎉 Nightcrawler installed');
  }
});

export {};
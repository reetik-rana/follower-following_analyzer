// Use window.chrome or browser for storage API
const storage = (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local)
  ? chrome.storage.local
  : (typeof browser !== 'undefined' && browser.storage && browser.storage.local)
    ? browser.storage.local
    : null;

let scrapeState = 0;
let followers = [];
let following = [];

const btn = document.getElementById('scrapeAnalyzeBtn');
const resultsDiv = document.getElementById('results');

// Restore state on popup open
if (storage) {
  storage.get(['followers', 'scrapeState'], (data) => {
    if (data.followers && Array.isArray(data.followers) && data.followers.length > 0) {
      followers = data.followers;
      scrapeState = data.scrapeState || 1;
      resultsDiv.innerText = `Followers scraped: ${followers.length}\nNow open your Following dialog and click the button again.`;
      btn.innerText = 'Scrape & Analyze (Following)';
    }
  });
}

function sendScrapeMessage(tabId) {
  chrome.tabs.sendMessage(tabId, {action: 'scrapeAndAnalyze'}, (response) => {
    if (chrome.runtime.lastError) {
      // Content script not injected, so inject it and retry
      chrome.scripting.executeScript({
        target: {tabId: tabId},
        files: ['content.js']
      }, () => {
        chrome.tabs.sendMessage(tabId, {action: 'scrapeAndAnalyze'});
      });
    }
  });
}

btn.addEventListener('click', async () => {
  document.getElementById('results').innerText = 'Navigating and scraping...';
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    sendScrapeMessage(tabs[0].id);
  });
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'showResults') {
    document.getElementById('results').innerText = message.result;
  }
});

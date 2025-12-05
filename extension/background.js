// Background service worker for MP3by4 Chrome Extension
// Required by Manifest V3

chrome.runtime.onInstalled.addListener(() => {
  console.log('MP3by4 extension installed');
});

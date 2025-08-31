// Background script for MP3by4 Chrome Extension
// Handles content extraction and tab management

chrome.runtime.onInstalled.addListener(() => {
  console.log('MP3by4 extension installed');
});

// Handle messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'extractContent') {
    // Get the active tab
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
      if (tabs[0]) {
        // Execute content script to extract page content
        chrome.scripting.executeScript({
          target: {tabId: tabs[0].id},
          function: extractPageContent
        }, (results) => {
          if (results && results[0]) {
            sendResponse({
              success: true,
              content: results[0].result,
              url: tabs[0].url,
              title: tabs[0].title
            });
          } else {
            sendResponse({
              success: false,
              error: 'Failed to extract content'
            });
          }
        });
      } else {
        sendResponse({
          success: false,
          error: 'No active tab found'
        });
      }
    });
    return true; // Keep message channel open for async response
  }
});

// Function to extract content from the current page
function extractPageContent() {
  try {
    // Get the main content
    let content = '';
    
    // Try to get article content first
    const article = document.querySelector('article');
    if (article) {
      content = article.textContent || article.innerText;
    } else {
      // Fallback to main content areas
      const main = document.querySelector('main');
      if (main) {
        content = main.textContent || main.innerText;
      } else {
        // Get content from common content containers
        const contentSelectors = [
          '.content',
          '.post-content',
          '.entry-content',
          '.article-content',
          '.story-content',
          '#content',
          '#main-content'
        ];
        
        for (const selector of contentSelectors) {
          const element = document.querySelector(selector);
          if (element) {
            content = element.textContent || element.innerText;
            break;
          }
        }
        
        // If still no content, get body text
        if (!content) {
          const body = document.body;
          content = body.textContent || body.innerText;
        }
      }
    }
    
    // Clean up the content
    content = content
      .replace(/\s+/g, ' ')
      .replace(/\n+/g, '\n')
      .trim();
    
    // Get page metadata
    const title = document.title || '';
    const description = document.querySelector('meta[name="description"]')?.content || '';
    const keywords = document.querySelector('meta[name="keywords"]')?.content || '';
    
    return {
      content: content,
      title: title,
      description: description,
      keywords: keywords,
      url: window.location.href,
      timestamp: new Date().toISOString()
    };
    
  } catch (error) {
    console.error('Error extracting content:', error);
    return {
      error: error.message,
      content: '',
      title: document.title || '',
      url: window.location.href
    };
  }
}

// Handle extension icon click
chrome.action.onClicked.addListener((tab) => {
  // This will open the popup when the extension icon is clicked
  console.log('Extension icon clicked on tab:', tab.id);
});

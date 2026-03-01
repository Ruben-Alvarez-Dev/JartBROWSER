// Background service worker for JartBROWSER Chrome extension

console.log('[JartBROWSER] Background service worker initialized');

// Install event
chrome.runtime.onInstalled.addListener((details) => {
  console.log('[JartBROWSER] Extension installed:', details.reason);
  
  if (details.reason === 'install') {
    // Open sidebar on first install
    chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
  }
});

// Command listeners
chrome.commands.onCommand.addListener((command) => {
  console.log('[JartBROWSER] Command received:', command);
  
  switch (command) {
    case 'toggle-sidebar':
      chrome.sidePanel.open({ windowId: chrome.windows.WINDOW_ID_CURRENT });
      break;
    case 'start-agent':
      chrome.runtime.sendMessage({ type: 'START_AGENT' });
      break;
  }
});

// Tab navigation tracking
chrome.webNavigation.onCompleted.addListener((details) => {
  if (details.frameId === 0) {
    console.log('[JartBROWSER] Page loaded:', details.url);
    chrome.storage.session.set({ currentUrl: details.url });
  }
});

// Message handler
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('[JartBROWSER] Message received:', message);
  
  switch (message.type) {
    case 'GET_PAGE_CONTENT':
      chrome.scripting.executeScript({
        target: { tabId: sender.tab.id },
        func: () => document.body.innerText
      }, (result) => {
        sendResponse({ content: result[0] });
      });
      return true; // async response
  }
  
  return false;
});

console.log('[JartBROWSER] Background service worker ready');

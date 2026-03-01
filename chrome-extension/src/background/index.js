// Background service worker for JartBROWSER Chrome extension

console.log('[JartBROWSER] Background service worker initialized');

// ============== State ==============
let currentTabId = null;
let currentUrl = '';
let currentTitle = '';

// ============== Install Event ==============
chrome.runtime.onInstalled.addListener((details) => {
  console.log('[JartBROWSER] Extension installed:', details.reason);
  
  if (details.reason === 'install') {
    // Open sidebar on first install
    chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
  }
});

// ============== Tab Tracking ==============
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  currentTabId = activeInfo.tabId;
  const tab = await chrome.tabs.get(activeInfo.tabId);
  currentUrl = tab.url || '';
  currentTitle = tab.title || '';
});

chrome.webNavigation.onCompleted.addListener((details) => {
  if (details.frameId === 0) {
    console.log('[JartBROWSER] Page loaded:', details.url);
    currentUrl = details.url;
    currentTabId = details.tabId;
  }
});

// ============== Command Listeners ==============
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

// ============== Message Handler ==============
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('[JartBROWSER] Message received:', message.type);
  
  switch (message.type) {
    case 'GET_PAGE_CONTENT':
      // Get page text content
      chrome.scripting.executeScript({
        target: { tabId: sender.tab.id },
        func: () => document.body.innerText
      }, (result) => {
        sendResponse({ content: result[0] });
      });
      return true;
    
    case 'GET_TAB_INFO':
      // Get current tab info
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]) {
          sendResponse({
            url: tabs[0].url,
            title: tabs[0].title
          });
        }
      });
      return true;
    
    case 'GET_ELEMENTS':
      // Get interactive elements
      chrome.scripting.executeScript({
        target: { tabId: sender.tab.id },
        func: () => {
          const elements = [];
          const selectors = ['a', 'button', 'input', 'select', 'textarea', '[role="button"]'];
          
          selectors.forEach(selector => {
            document.querySelectorAll(selector).forEach((el, index) => {
              const rect = el.getBoundingClientRect();
              if (rect.width > 0 && rect.height > 0) {
                // Generate unique selector
                let sel = el.tagName.toLowerCase();
                if (el.id) sel += '#' + el.id;
                else if (el.className) sel += '.' + el.className.split(' ')[0];
                else sel += ':nth-of-type(' + (index + 1) + ')';
                
                elements.push({
                  tag: el.tagName.toLowerCase(),
                  selector: sel,
                  text: el.innerText?.substring(0, 50) || el.value?.substring(0, 50) || ''
                });
              }
            });
          });
          
          return elements.slice(0, 50); // Limit to 50 elements
        }
      }, (result) => {
        sendResponse({ elements: result[0] });
      });
      return true;
    
    case 'NAVIGATE':
      // Navigate to URL
      chrome.tabs.update(sender.tab.id, { url: message.url });
      sendResponse({ success: true });
      return false;
    
    case 'EXECUTE_ACTION':
      // Execute browser action
      const { action, target, value } = message;
      
      switch (action) {
        case 'click':
          chrome.scripting.executeScript({
            target: { tabId: sender.tab.id },
            func: (sel) => {
              const el = document.querySelector(sel);
              if (el) el.click();
            },
            args: [target]
          });
          break;
        case 'fill':
          chrome.scripting.executeScript({
            target: { tabId: sender.tab.id },
            func: (sel, val) => {
              const el = document.querySelector(sel);
              if (el) {
                el.value = val;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
              }
            },
            args: [target, value]
          });
          break;
        case 'screenshot':
          // Would use chrome.tabs.captureVisibleTab
          break;
        case 'scroll-top':
          chrome.scripting.executeScript({
            target: { tabId: sender.tab.id },
            func: () => window.scrollTo(0, 0)
          });
          break;
        case 'scroll-bottom':
          chrome.scripting.executeScript({
            target: { tabId: sender.tab.id },
            func: () => window.scrollTo(0, document.body.scrollHeight)
          });
          break;
      }
      
      sendResponse({ success: true });
      return false;
  }
  
  return false;
});

console.log('[JartBROWSER] Background service worker ready');

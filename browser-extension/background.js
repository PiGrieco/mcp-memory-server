/**
 * Production-Ready Background Service Worker for MCP Memory Browser Extension
 * Enhanced with error handling, retry logic, and cloud synchronization
 */

// Configuration
const CONFIG = {
  SERVER_URL: 'http://localhost:8000',
  CLOUD_SYNC_ENABLED: true,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
  SYNC_INTERVAL: 300000, // 5 minutes
  BATCH_SIZE: 10,
  MAX_MEMORY_SIZE: 1000000, // 1MB
  SUPPORTED_PLATFORMS: [
    'chat.openai.com',
    'claude.ai',
    'poe.com',
    'perplexity.ai',
    'bing.com',
    'bard.google.com'
  ]
};

// State management
let memoryCache = new Map();
let syncQueue = [];
let isOnline = navigator.onLine;
let lastSyncTime = 0;

/**
 * Error handling and logging
 */
class Logger {
  static log(level, message, data = null) {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      level,
      message,
      data,
      url: self.location?.href || 'background'
    };
    
    console[level](`[MCP Memory ${level.toUpperCase()}] ${message}`, data || '');
    
    // Store logs for debugging
    chrome.storage.local.get(['logs'], (result) => {
      const logs = result.logs || [];
      logs.push(logEntry);
      
      // Keep only last 100 logs
      if (logs.length > 100) {
        logs.splice(0, logs.length - 100);
      }
      
      chrome.storage.local.set({ logs });
    });
  }
  
  static info(message, data) { this.log('info', message, data); }
  static warn(message, data) { this.log('warn', message, data); }
  static error(message, data) { this.log('error', message, data); }
  static debug(message, data) { this.log('debug', message, data); }
}

/**
 * HTTP client with retry logic and error handling
 */
class HttpClient {
  static async request(method, endpoint, data = null, options = {}) {
    const { retries = CONFIG.RETRY_ATTEMPTS, delay = CONFIG.RETRY_DELAY } = options;
    
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const url = `${CONFIG.SERVER_URL}${endpoint}`;
        const config = {
          method,
          headers: {
            'Content-Type': 'application/json',
            'X-Extension-Version': chrome.runtime.getManifest().version,
            'X-Platform': 'browser-extension'
          },
          ...options
        };
        
        if (data) {
          config.body = JSON.stringify(data);
        }
        
        // Add API key if available
        const settings = await this.getSettings();
        if (settings.apiKey) {
          config.headers['Authorization'] = `Bearer ${settings.apiKey}`;
        }
        
        const response = await fetch(url, config);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        Logger.debug(`${method} ${endpoint} success`, { attempt, result });
        
        return result;
        
      } catch (error) {
        Logger.warn(`${method} ${endpoint} attempt ${attempt} failed`, { error: error.message });
        
        if (attempt === retries) {
          Logger.error(`${method} ${endpoint} failed after ${retries} attempts`, { error: error.message });
          throw error;
        }
        
        // Exponential backoff
        await this.delay(delay * Math.pow(2, attempt - 1));
      }
    }
  }
  
  static async getSettings() {
    return new Promise((resolve) => {
      chrome.storage.sync.get({
        apiKey: '',
        serverUrl: CONFIG.SERVER_URL,
        cloudSync: CONFIG.CLOUD_SYNC_ENABLED,
        autoSave: true,
        project: 'default'
      }, resolve);
    });
  }
  
  static delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

/**
 * Memory management with caching and validation
 */
class MemoryManager {
  static async saveMemory(memory) {
    try {
      // Validate memory
      if (!this.validateMemory(memory)) {
        throw new Error('Invalid memory format');
      }
      
      // Enhance memory with metadata
      const enhancedMemory = {
        ...memory,
        id: memory.id || this.generateId(),
        timestamp: new Date().toISOString(),
        source: 'browser-extension',
        platform: this.detectPlatform(memory.url || ''),
        version: chrome.runtime.getManifest().version
      };
      
      // Add to cache
      memoryCache.set(enhancedMemory.id, enhancedMemory);
      
      // Try to save to server
      try {
        const result = await HttpClient.request('POST', '/memories', enhancedMemory);
        Logger.info('Memory saved to server', { id: enhancedMemory.id });
        return result;
      } catch (error) {
        // Add to sync queue for later
        syncQueue.push({ action: 'save', memory: enhancedMemory });
        Logger.warn('Memory queued for sync', { id: enhancedMemory.id, error: error.message });
        
        // Save to local storage as backup
        await this.saveToLocal(enhancedMemory);
        return { success: true, queued: true };
      }
      
    } catch (error) {
      Logger.error('Failed to save memory', { error: error.message, memory });
      throw error;
    }
  }
  
  static async searchMemories(query, options = {}) {
    try {
      const searchParams = {
        query,
        project: options.project || 'default',
        limit: options.limit || 10,
        similarity_threshold: options.threshold || 0.3
      };
      
      // Try server first
      try {
        const result = await HttpClient.request('POST', '/memories/search', searchParams);
        Logger.debug('Memory search from server', { query, count: result.memories?.length });
        return result.memories || [];
      } catch (error) {
        Logger.warn('Server search failed, using local cache', { error: error.message });
        return this.searchLocal(query, options);
      }
      
    } catch (error) {
      Logger.error('Memory search failed', { error: error.message, query });
      return [];
    }
  }
  
  static async searchLocal(query, options = {}) {
    const memories = Array.from(memoryCache.values());
    const queryLower = query.toLowerCase();
    
    return memories
      .filter(memory => 
        memory.content.toLowerCase().includes(queryLower) ||
        memory.title?.toLowerCase().includes(queryLower)
      )
      .slice(0, options.limit || 10);
  }
  
  static validateMemory(memory) {
    if (!memory || typeof memory !== 'object') return false;
    if (!memory.content || typeof memory.content !== 'string') return false;
    if (memory.content.length > CONFIG.MAX_MEMORY_SIZE) return false;
    return true;
  }
  
  static detectPlatform(url) {
    for (const platform of CONFIG.SUPPORTED_PLATFORMS) {
      if (url.includes(platform)) {
        return platform;
      }
    }
    return 'unknown';
  }
  
  static generateId() {
    return `mem_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  static async saveToLocal(memory) {
    const key = `memory_${memory.id}`;
    await chrome.storage.local.set({ [key]: memory });
  }
  
  static async loadFromLocal() {
    return new Promise((resolve) => {
      chrome.storage.local.get(null, (items) => {
        const memories = [];
        for (const [key, value] of Object.entries(items)) {
          if (key.startsWith('memory_') && value.id) {
            memories.push(value);
          }
        }
        resolve(memories);
      });
    });
  }
}

/**
 * Cloud synchronization manager
 */
class SyncManager {
  static async performSync() {
    if (!isOnline || syncQueue.length === 0) return;
    
    Logger.info('Starting sync', { queueSize: syncQueue.length });
    
    const batch = syncQueue.splice(0, CONFIG.BATCH_SIZE);
    const results = [];
    
    for (const item of batch) {
      try {
        if (item.action === 'save') {
          const result = await HttpClient.request('POST', '/memories', item.memory);
          results.push({ success: true, id: item.memory.id });
        }
      } catch (error) {
        // Put back in queue
        syncQueue.unshift(item);
        Logger.warn('Sync item failed, requeued', { error: error.message });
      }
    }
    
    lastSyncTime = Date.now();
    Logger.info('Sync completed', { processed: results.length, remaining: syncQueue.length });
    
    return results;
  }
  
  static async scheduleSync() {
    const now = Date.now();
    if (now - lastSyncTime > CONFIG.SYNC_INTERVAL) {
      await this.performSync();
    }
  }
}

/**
 * Platform-specific integrations
 */
class PlatformIntegrations {
  static async injectMemoryWidget(tabId, platform) {
    try {
      // Inject platform-specific memory widget
      await chrome.scripting.executeScript({
        target: { tabId },
        files: [`integrations/${platform}.js`]
      });
      
      Logger.info('Memory widget injected', { tabId, platform });
    } catch (error) {
      Logger.warn('Failed to inject memory widget', { error: error.message, tabId, platform });
    }
  }
  
  static async enhanceConversation(tabId, conversationData) {
    try {
      // Search for relevant memories
      const relevantMemories = await MemoryManager.searchMemories(
        conversationData.lastMessage, 
        { limit: 5, threshold: 0.5 }
      );
      
      if (relevantMemories.length > 0) {
        // Send memories to content script
        await chrome.tabs.sendMessage(tabId, {
          type: 'RELEVANT_MEMORIES',
          memories: relevantMemories,
          conversation: conversationData
        });
        
        Logger.debug('Sent relevant memories to tab', { tabId, count: relevantMemories.length });
      }
    } catch (error) {
      Logger.warn('Failed to enhance conversation', { error: error.message });
    }
  }
}

/**
 * Event listeners and initialization
 */

// Extension installation/update
chrome.runtime.onInstalled.addListener(async (details) => {
  Logger.info('Extension installed/updated', { reason: details.reason, version: chrome.runtime.getManifest().version });
  
  if (details.reason === 'install') {
    // First time setup
    await chrome.storage.sync.set({
      apiKey: '',
      serverUrl: CONFIG.SERVER_URL,
      cloudSync: true,
      autoSave: true,
      project: 'default',
      setupComplete: false
    });
    
    // Open setup page
    chrome.tabs.create({ url: chrome.runtime.getURL('setup.html') });
  }
  
  // Load local memories into cache
  const localMemories = await MemoryManager.loadFromLocal();
  localMemories.forEach(memory => memoryCache.set(memory.id, memory));
  Logger.info('Loaded local memories', { count: localMemories.length });
  
  // Setup periodic sync
  chrome.alarms.create('sync', { periodInMinutes: 5 });
});

// Tab navigation - inject memory widgets
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url) {
    const platform = MemoryManager.detectPlatform(tab.url);
    if (platform !== 'unknown') {
      await PlatformIntegrations.injectMemoryWidget(tabId, platform);
    }
  }
});

// Message handling from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  handleMessage(message, sender).then(sendResponse).catch(error => {
    Logger.error('Message handling failed', { error: error.message, message });
    sendResponse({ success: false, error: error.message });
  });
  return true; // Async response
});

async function handleMessage(message, sender) {
  const { type, data } = message;
  
  switch (type) {
    case 'SAVE_MEMORY':
      return await MemoryManager.saveMemory(data);
      
    case 'SEARCH_MEMORIES':
      return await MemoryManager.searchMemories(data.query, data.options);
      
    case 'GET_RELEVANT_MEMORIES':
      const memories = await MemoryManager.searchMemories(data.context, { limit: 5 });
      return { memories };
      
    case 'CONVERSATION_UPDATE':
      if (sender.tab?.id) {
        await PlatformIntegrations.enhanceConversation(sender.tab.id, data);
      }
      return { success: true };
      
    case 'GET_SETTINGS':
      return await HttpClient.getSettings();
      
    case 'FORCE_SYNC':
      return await SyncManager.performSync();
      
    case 'GET_STATUS':
      return {
        isOnline,
        cacheSize: memoryCache.size,
        queueSize: syncQueue.length,
        lastSyncTime
      };
      
    default:
      throw new Error(`Unknown message type: ${type}`);
  }
}

// Periodic sync
chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === 'sync') {
    await SyncManager.scheduleSync();
  }
});

// Network status monitoring
chrome.runtime.onConnect.addListener((port) => {
  if (port.name === 'network-status') {
    const updateNetworkStatus = () => {
      isOnline = navigator.onLine;
      port.postMessage({ type: 'NETWORK_STATUS', isOnline });
    };
    
    window.addEventListener('online', updateNetworkStatus);
    window.addEventListener('offline', updateNetworkStatus);
    
    // Send initial status
    updateNetworkStatus();
  }
});

// Error boundary
self.addEventListener('error', (event) => {
  Logger.error('Unhandled error in background script', {
    message: event.message,
    filename: event.filename,
    lineno: event.lineno,
    colno: event.colno
  });
});

self.addEventListener('unhandledrejection', (event) => {
  Logger.error('Unhandled promise rejection in background script', {
    reason: event.reason
  });
});

// Initialize
Logger.info('Background script loaded', { 
  version: chrome.runtime.getManifest().version,
  config: CONFIG 
});

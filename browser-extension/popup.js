/**
 * Production-Ready Popup Script for MCP Memory Browser Extension
 * Enhanced UI interactions and settings management
 */

// DOM elements
const elements = {
  connectionIndicator: document.getElementById('connection-indicator'),
  connectionStatus: document.getElementById('connection-status'),
  serverUrl: document.getElementById('server-url'),
  currentProject: document.getElementById('current-project'),
  memoryCount: document.getElementById('memory-count'),
  queueSize: document.getElementById('queue-size'),
  syncStatus: document.getElementById('sync-status'),
  alertContainer: document.getElementById('alert-container'),
  
  // Action buttons
  saveConversation: document.getElementById('save-conversation'),
  forceSync: document.getElementById('force-sync'),
  searchMemories: document.getElementById('search-memories'),
  openSettings: document.getElementById('open-settings'),
  
  // Settings
  autoSaveToggle: document.getElementById('auto-save-toggle'),
  cloudSyncToggle: document.getElementById('cloud-sync-toggle'),
  serverUrlInput: document.getElementById('server-url-input'),
  apiKeyInput: document.getElementById('api-key-input'),
  projectInput: document.getElementById('project-input'),
  
  // Footer links
  openDocs: document.getElementById('open-docs'),
  openSupport: document.getElementById('open-support'),
  viewLogs: document.getElementById('view-logs')
};

// State management
let currentSettings = {};
let statusUpdateInterval = null;

/**
 * Utility functions
 */
class PopupUtils {
  static showAlert(message, type = 'info', duration = 5000) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    elements.alertContainer.appendChild(alert);
    
    // Auto-remove after duration
    setTimeout(() => {
      if (alert.parentElement) {
        alert.remove();
      }
    }, duration);
  }
  
  static setLoading(element, loading = true) {
    if (loading) {
      element.classList.add('loading');
      element.disabled = true;
    } else {
      element.classList.remove('loading');
      element.disabled = false;
    }
  }
  
  static formatTimestamp(timestamp) {
    if (!timestamp) return '--';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
  }
  
  static async sendMessage(message) {
    return new Promise((resolve) => {
      chrome.runtime.sendMessage(message, (response) => {
        if (chrome.runtime.lastError) {
          console.error('Message error:', chrome.runtime.lastError);
          resolve({ success: false, error: chrome.runtime.lastError.message });
        } else {
          resolve(response || { success: false, error: 'No response' });
        }
      });
    });
  }
  
  static async getCurrentTab() {
    return new Promise((resolve) => {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        resolve(tabs[0] || null);
      });
    });
  }
}

/**
 * Settings management
 */
class SettingsManager {
  static async load() {
    return new Promise((resolve) => {
      chrome.storage.sync.get({
        apiKey: '',
        serverUrl: 'http://localhost:8000',
        cloudSync: true,
        autoSave: true,
        project: 'default',
        setupComplete: false
      }, (settings) => {
        currentSettings = settings;
        resolve(settings);
      });
    });
  }
  
  static async save(updates) {
    return new Promise((resolve) => {
      const newSettings = { ...currentSettings, ...updates };
      chrome.storage.sync.set(newSettings, () => {
        currentSettings = newSettings;
        resolve(newSettings);
      });
    });
  }
  
  static async updateUI() {
    // Update input fields
    elements.serverUrlInput.value = currentSettings.serverUrl || '';
    elements.apiKeyInput.value = currentSettings.apiKey || '';
    elements.projectInput.value = currentSettings.project || 'default';
    
    // Update toggles
    elements.autoSaveToggle.classList.toggle('active', currentSettings.autoSave);
    elements.cloudSyncToggle.classList.toggle('active', currentSettings.cloudSync);
    
    // Update display values
    elements.serverUrl.textContent = currentSettings.serverUrl || 'Not configured';
    elements.currentProject.textContent = currentSettings.project || 'default';
  }
}

/**
 * Status monitoring
 */
class StatusMonitor {
  static async updateStatus() {
    try {
      const status = await PopupUtils.sendMessage({ type: 'GET_STATUS' });
      
      if (status.success !== false) {
        // Update connection status
        elements.connectionIndicator.className = `status-indicator ${status.isOnline ? 'status-online' : 'status-offline'}`;
        elements.connectionStatus.textContent = status.isOnline ? 'Connected' : 'Offline';
        
        // Update stats
        elements.memoryCount.textContent = status.cacheSize || 0;
        elements.queueSize.textContent = status.queueSize || 0;
        elements.syncStatus.textContent = PopupUtils.formatTimestamp(status.lastSyncTime);
        
        // Update sync status indicator
        if (status.queueSize > 0) {
          elements.connectionIndicator.className = 'status-indicator status-syncing';
        }
      } else {
        // Handle error state
        elements.connectionIndicator.className = 'status-indicator status-offline';
        elements.connectionStatus.textContent = 'Error';
      }
      
    } catch (error) {
      console.error('Status update failed:', error);
      elements.connectionIndicator.className = 'status-indicator status-offline';
      elements.connectionStatus.textContent = 'Disconnected';
    }
  }
  
  static startMonitoring() {
    // Initial update
    this.updateStatus();
    
    // Update every 5 seconds
    statusUpdateInterval = setInterval(() => {
      this.updateStatus();
    }, 5000);
  }
  
  static stopMonitoring() {
    if (statusUpdateInterval) {
      clearInterval(statusUpdateInterval);
      statusUpdateInterval = null;
    }
  }
}

/**
 * Action handlers
 */
class ActionHandlers {
  static async saveConversation() {
    try {
      PopupUtils.setLoading(elements.saveConversation, true);
      
      const tab = await PopupUtils.getCurrentTab();
      if (!tab) {
        PopupUtils.showAlert('No active tab found', 'error');
        return;
      }
      
      // Send message to content script
      const response = await new Promise((resolve) => {
        chrome.tabs.sendMessage(tab.id, {
          type: 'SAVE_CONVERSATION',
          manual: true
        }, resolve);
      });
      
      if (response && response.success) {
        PopupUtils.showAlert('Conversation saved successfully!', 'success');
      } else {
        PopupUtils.showAlert('Failed to save conversation', 'error');
      }
      
    } catch (error) {
      console.error('Save conversation failed:', error);
      PopupUtils.showAlert('Save operation failed', 'error');
    } finally {
      PopupUtils.setLoading(elements.saveConversation, false);
    }
  }
  
  static async forceSync() {
    try {
      PopupUtils.setLoading(elements.forceSync, true);
      
      const response = await PopupUtils.sendMessage({ type: 'FORCE_SYNC' });
      
      if (response.success !== false) {
        PopupUtils.showAlert('Synchronization completed', 'success');
        StatusMonitor.updateStatus(); // Refresh status
      } else {
        PopupUtils.showAlert('Synchronization failed', 'error');
      }
      
    } catch (error) {
      console.error('Force sync failed:', error);
      PopupUtils.showAlert('Sync operation failed', 'error');
    } finally {
      PopupUtils.setLoading(elements.forceSync, false);
    }
  }
  
  static async searchMemories() {
    try {
      // Open search interface in new tab
      chrome.tabs.create({
        url: chrome.runtime.getURL('search.html')
      });
      
    } catch (error) {
      console.error('Search memories failed:', error);
      PopupUtils.showAlert('Failed to open search', 'error');
    }
  }
  
  static async openSettings() {
    try {
      // Open options page
      chrome.runtime.openOptionsPage();
      
    } catch (error) {
      console.error('Open settings failed:', error);
      PopupUtils.showAlert('Failed to open settings', 'error');
    }
  }
  
  static async toggleAutoSave() {
    const newValue = !currentSettings.autoSave;
    await SettingsManager.save({ autoSave: newValue });
    elements.autoSaveToggle.classList.toggle('active', newValue);
    
    PopupUtils.showAlert(
      `Auto-save ${newValue ? 'enabled' : 'disabled'}`, 
      'success'
    );
  }
  
  static async toggleCloudSync() {
    const newValue = !currentSettings.cloudSync;
    await SettingsManager.save({ cloudSync: newValue });
    elements.cloudSyncToggle.classList.toggle('active', newValue);
    
    PopupUtils.showAlert(
      `Cloud sync ${newValue ? 'enabled' : 'disabled'}`, 
      'success'
    );
  }
  
  static async updateServerUrl() {
    const newUrl = elements.serverUrlInput.value.trim();
    if (newUrl && newUrl !== currentSettings.serverUrl) {
      await SettingsManager.save({ serverUrl: newUrl });
      elements.serverUrl.textContent = newUrl;
      PopupUtils.showAlert('Server URL updated', 'success');
    }
  }
  
  static async updateApiKey() {
    const newKey = elements.apiKeyInput.value.trim();
    if (newKey !== currentSettings.apiKey) {
      await SettingsManager.save({ apiKey: newKey });
      PopupUtils.showAlert('API key updated', 'success');
    }
  }
  
  static async updateProject() {
    const newProject = elements.projectInput.value.trim() || 'default';
    if (newProject !== currentSettings.project) {
      await SettingsManager.save({ project: newProject });
      elements.currentProject.textContent = newProject;
      PopupUtils.showAlert('Project updated', 'success');
    }
  }
  
  static async openDocs() {
    chrome.tabs.create({
      url: 'https://github.com/your-repo/mcp-memory-server#documentation'
    });
  }
  
  static async openSupport() {
    chrome.tabs.create({
      url: 'https://github.com/your-repo/mcp-memory-server/issues'
    });
  }
  
  static async viewLogs() {
    try {
      chrome.tabs.create({
        url: chrome.runtime.getURL('logs.html')
      });
    } catch (error) {
      PopupUtils.showAlert('Failed to open logs', 'error');
    }
  }
}

/**
 * Event listeners setup
 */
function setupEventListeners() {
  // Action buttons
  elements.saveConversation.addEventListener('click', ActionHandlers.saveConversation);
  elements.forceSync.addEventListener('click', ActionHandlers.forceSync);
  elements.searchMemories.addEventListener('click', ActionHandlers.searchMemories);
  elements.openSettings.addEventListener('click', ActionHandlers.openSettings);
  
  // Settings toggles
  elements.autoSaveToggle.addEventListener('click', ActionHandlers.toggleAutoSave);
  elements.cloudSyncToggle.addEventListener('click', ActionHandlers.toggleCloudSync);
  
  // Input fields with debounced updates
  let updateTimeout;
  
  elements.serverUrlInput.addEventListener('input', () => {
    clearTimeout(updateTimeout);
    updateTimeout = setTimeout(ActionHandlers.updateServerUrl, 1000);
  });
  
  elements.apiKeyInput.addEventListener('input', () => {
    clearTimeout(updateTimeout);
    updateTimeout = setTimeout(ActionHandlers.updateApiKey, 1000);
  });
  
  elements.projectInput.addEventListener('input', () => {
    clearTimeout(updateTimeout);
    updateTimeout = setTimeout(ActionHandlers.updateProject, 1000);
  });
  
  // Footer links
  elements.openDocs.addEventListener('click', ActionHandlers.openDocs);
  elements.openSupport.addEventListener('click', ActionHandlers.openSupport);
  elements.viewLogs.addEventListener('click', ActionHandlers.viewLogs);
  
  // Handle popup close
  window.addEventListener('beforeunload', () => {
    StatusMonitor.stopMonitoring();
  });
}

/**
 * Initialization
 */
async function initialize() {
  try {
    // Load settings
    await SettingsManager.load();
    await SettingsManager.updateUI();
    
    // Setup event listeners
    setupEventListeners();
    
    // Start status monitoring
    StatusMonitor.startMonitoring();
    
    // Check if setup is complete
    if (!currentSettings.setupComplete) {
      PopupUtils.showAlert(
        'Complete setup by configuring your server URL and API key', 
        'warning', 
        10000
      );
    }
    
    console.log('MCP Memory popup initialized');
    
  } catch (error) {
    console.error('Popup initialization failed:', error);
    PopupUtils.showAlert('Initialization failed', 'error');
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initialize);
} else {
  initialize();
}

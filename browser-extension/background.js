// MCP Memory Extension - Background Service Worker

class BackgroundService {
    constructor() {
        this.apiBase = 'http://localhost:8000';
        this.init();
    }

    init() {
        // Set default settings on installation
        chrome.runtime.onInstalled.addListener((details) => {
            if (details.reason === 'install') {
                this.setDefaultSettings();
                this.showWelcomeNotification();
            } else if (details.reason === 'update') {
                this.showUpdateNotification();
            }
        });

        // Handle messages from content scripts and popup
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            this.handleMessage(message, sender, sendResponse);
            return true; // Keep message channel open for async responses
        });

        // Monitor tab updates to inject content script
        chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
            if (changeInfo.status === 'complete' && this.isChatGPTTab(tab.url)) {
                this.injectContentScript(tabId);
            }
        });

        // Context menu for quick actions
        this.setupContextMenu();

        // Periodic health check
        this.setupHealthCheck();
    }

    async setDefaultSettings() {
        const defaultSettings = {
            autoSave: true,
            suggestions: true,
            notifications: true,
            apiUrl: this.apiBase,
            firstTime: true
        };

        await chrome.storage.sync.set(defaultSettings);
        await chrome.storage.local.set({
            autoSaves: 0,
            searches: 0,
            sessionsTracked: 0
        });
    }

    showWelcomeNotification() {
        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon48.png',
            title: '🧠 MCP Memory Installed!',
            message: 'Your ChatGPT now has persistent memory. Visit ChatGPT to get started!'
        });
    }

    showUpdateNotification() {
        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon48.png',
            title: '🚀 MCP Memory Updated!',
            message: 'New features and improvements are now available.'
        });
    }

    async handleMessage(message, sender, sendResponse) {
        try {
            switch (message.action) {
                case 'checkConnection':
                    const isConnected = await this.checkAPIConnection();
                    sendResponse({ connected: isConnected });
                    break;

                case 'saveMemory':
                    const saveResult = await this.saveMemory(message.data);
                    this.updateStats('autoSaves');
                    sendResponse(saveResult);
                    break;

                case 'searchMemory':
                    const searchResult = await this.searchMemory(message.query);
                    this.updateStats('searches');
                    sendResponse(searchResult);
                    break;

                case 'getStats':
                    const stats = await this.getStats();
                    sendResponse(stats);
                    break;

                case 'updateBadge':
                    this.updateBadge(message.count);
                    break;

                default:
                    sendResponse({ error: 'Unknown action' });
            }
        } catch (error) {
            console.error('Background service error:', error);
            sendResponse({ error: error.message });
        }
    }

    async checkAPIConnection() {
        try {
            const response = await fetch(`${this.apiBase}/docs`, {
                method: 'GET',
                signal: AbortSignal.timeout(3000)
            });
            return response.ok;
        } catch (error) {
            return false;
        }
    }

    async saveMemory(data) {
        try {
            const response = await fetch(`${this.apiBase}/save`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            
            if (response.ok) {
                this.showMemoryNotification('💾 Memory Saved', `Saved: ${data.text.substring(0, 50)}...`);
                return { success: true, data: result };
            } else {
                throw new Error(result.error || 'Save failed');
            }
        } catch (error) {
            console.error('Save memory error:', error);
            return { success: false, error: error.message };
        }
    }

    async searchMemory(query) {
        try {
            const response = await fetch(`${this.apiBase}/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
                    project: 'chatgpt',
                    limit: 10
                })
            });

            const result = await response.json();
            
            if (response.ok) {
                return { success: true, data: result };
            } else {
                throw new Error(result.error || 'Search failed');
            }
        } catch (error) {
            console.error('Search memory error:', error);
            return { success: false, error: error.message };
        }
    }

    async updateStats(type) {
        const current = await chrome.storage.local.get([type]);
        const newValue = (current[type] || 0) + 1;
        await chrome.storage.local.set({ [type]: newValue });
        
        // Update badge with total activity
        const stats = await chrome.storage.local.get(['autoSaves', 'searches']);
        const total = (stats.autoSaves || 0) + (stats.searches || 0);
        this.updateBadge(total);
    }

    async getStats() {
        return await chrome.storage.local.get(['autoSaves', 'searches', 'sessionsTracked']);
    }

    updateBadge(count) {
        if (count > 0) {
            chrome.action.setBadgeText({
                text: count > 99 ? '99+' : count.toString()
            });
            chrome.action.setBadgeBackgroundColor({
                color: '#667eea'
            });
        } else {
            chrome.action.setBadgeText({ text: '' });
        }
    }

    isChatGPTTab(url) {
        return url && (url.includes('chat.openai.com') || url.includes('chatgpt.com'));
    }

    async injectContentScript(tabId) {
        try {
            // Check if content script is already injected
            const results = await chrome.scripting.executeScript({
                target: { tabId },
                function: () => window.mcpMemoryInjected === true
            });

            if (!results[0].result) {
                // Inject content script
                await chrome.scripting.executeScript({
                    target: { tabId },
                    files: ['content.js']
                });

                await chrome.scripting.insertCSS({
                    target: { tabId },
                    files: ['memory-ui.css']
                });
            }
        } catch (error) {
            console.error('Failed to inject content script:', error);
        }
    }

    setupContextMenu() {
        chrome.contextMenus.create({
            id: 'saveSelection',
            title: '💾 Save to Memory',
            contexts: ['selection'],
            documentUrlPatterns: ['*://chat.openai.com/*', '*://chatgpt.com/*']
        });

        chrome.contextMenus.create({
            id: 'searchMemory',
            title: '🔍 Search Memory',
            contexts: ['page'],
            documentUrlPatterns: ['*://chat.openai.com/*', '*://chatgpt.com/*']
        });

        chrome.contextMenus.onClicked.addListener((info, tab) => {
            this.handleContextMenuClick(info, tab);
        });
    }

    async handleContextMenuClick(info, tab) {
        try {
            if (info.menuItemId === 'saveSelection') {
                const result = await this.saveMemory({
                    text: info.selectionText,
                    memory_type: 'manual_selection',
                    project: 'chatgpt',
                    importance: 0.7
                });

                if (result.success) {
                    this.showMemoryNotification('💾 Selection Saved', 'Selected text saved to memory');
                }
            } else if (info.menuItemId === 'searchMemory') {
                // Send message to content script to show search dialog
                chrome.tabs.sendMessage(tab.id, {
                    action: 'showSearchDialog'
                });
            }
        } catch (error) {
            console.error('Context menu action failed:', error);
        }
    }

    setupHealthCheck() {
        // Check API connection every 5 minutes
        setInterval(async () => {
            const isConnected = await this.checkAPIConnection();
            
            // Update badge color based on connection status
            if (isConnected) {
                chrome.action.setBadgeBackgroundColor({ color: '#48bb78' });
            } else {
                chrome.action.setBadgeBackgroundColor({ color: '#f56565' });
            }
        }, 5 * 60 * 1000);
    }

    async showMemoryNotification(title, message) {
        const settings = await chrome.storage.sync.get(['notifications']);
        
        if (settings.notifications !== false) {
            chrome.notifications.create({
                type: 'basic',
                iconUrl: 'icons/icon48.png',
                title: title,
                message: message
            });
        }
    }
}

// Initialize background service
new BackgroundService(); 
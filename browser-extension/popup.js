// MCP Memory Extension - Popup Script

class PopupController {
    constructor() {
        this.apiBase = 'http://localhost:8000';
        this.init();
    }

    async init() {
        await this.checkConnection();
        await this.loadStats();
        this.setupEventListeners();
        this.loadSettings();
    }

    async checkConnection() {
        const statusIndicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');

        try {
            const response = await fetch(`${this.apiBase}/docs`, {
                method: 'GET',
                timeout: 3000
            });

            if (response.ok) {
                statusIndicator.classList.remove('disconnected');
                statusText.textContent = 'Connected to MCP Memory Server';
            } else {
                throw new Error('Server not responding');
            }
        } catch (error) {
            statusIndicator.classList.add('disconnected');
            statusText.innerHTML = `
                <div style="margin-bottom: 8px;">❌ Server not found</div>
                <div style="font-size: 11px; opacity: 0.8;">
                    Run: <code style="background: rgba(255,255,255,0.2); padding: 2px 4px; border-radius: 3px;">python examples/gpt_smart_auto.py</code>
                </div>
            `;
        }
    }

    async loadStats() {
        try {
            // Get stats from storage
            const result = await chrome.storage.local.get(['autoSaves', 'searches']);
            
            document.getElementById('autoSavesCount').textContent = result.autoSaves || 0;
            document.getElementById('searchesCount').textContent = result.searches || 0;

            // Try to get real-time stats from API
            const response = await fetch(`${this.apiBase}/analytics/session`, {
                method: 'GET'
            });

            if (response.ok) {
                const data = await response.json();
                if (data.auto_saves) {
                    document.getElementById('autoSavesCount').textContent = data.auto_saves;
                }
                if (data.searches) {
                    document.getElementById('searchesCount').textContent = data.searches;
                }
            }
        } catch (error) {
            console.log('Could not load real-time stats:', error);
        }
    }

    setupEventListeners() {
        // Search button
        document.getElementById('searchBtn').addEventListener('click', () => {
            this.showSearchDialog();
        });

        // Manual save button
        document.getElementById('manualSaveBtn').addEventListener('click', () => {
            this.manualSave();
        });

        // Dashboard button
        document.getElementById('openDashboardBtn').addEventListener('click', () => {
            chrome.tabs.create({ url: `${this.apiBase}/docs` });
        });

        // Toggle switches
        document.getElementById('autoSaveToggle').addEventListener('click', (e) => {
            this.toggleSetting('autoSave', e.target);
        });

        document.getElementById('suggestionsToggle').addEventListener('click', (e) => {
            this.toggleSetting('suggestions', e.target);
        });

        document.getElementById('notificationsToggle').addEventListener('click', (e) => {
            this.toggleSetting('notifications', e.target);
        });

        // Footer links
        document.getElementById('helpLink').addEventListener('click', () => {
            chrome.tabs.create({ url: 'https://github.com/AiGotsrl/mcp-memory-server/blob/main/PLUGIN_ECOSYSTEM.md' });
        });

        document.getElementById('githubLink').addEventListener('click', () => {
            chrome.tabs.create({ url: 'https://github.com/AiGotsrl/mcp-memory-server' });
        });

        document.getElementById('settingsLink').addEventListener('click', () => {
            chrome.runtime.openOptionsPage();
        });
    }

    async loadSettings() {
        const settings = await chrome.storage.sync.get([
            'autoSave', 'suggestions', 'notifications'
        ]);

        // Set toggle states
        this.setToggleState('autoSaveToggle', settings.autoSave !== false);
        this.setToggleState('suggestionsToggle', settings.suggestions !== false);
        this.setToggleState('notificationsToggle', settings.notifications !== false);
    }

    setToggleState(toggleId, isActive) {
        const toggle = document.getElementById(toggleId);
        if (isActive) {
            toggle.classList.add('active');
        } else {
            toggle.classList.remove('active');
        }
    }

    async toggleSetting(setting, toggleElement) {
        const isActive = !toggleElement.classList.contains('active');
        
        if (isActive) {
            toggleElement.classList.add('active');
        } else {
            toggleElement.classList.remove('active');
        }

        // Save to storage
        await chrome.storage.sync.set({ [setting]: isActive });

        // Send message to content script
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            if (tab && (tab.url.includes('chat.openai.com') || tab.url.includes('chatgpt.com'))) {
                chrome.tabs.sendMessage(tab.id, {
                    action: 'updateSetting',
                    setting: setting,
                    value: isActive
                });
            }
        } catch (error) {
            console.log('Could not send message to content script:', error);
        }

        this.showToast(`${setting.charAt(0).toUpperCase() + setting.slice(1)} ${isActive ? 'enabled' : 'disabled'}`);
    }

    showSearchDialog() {
        const query = prompt('🔍 Search your memory:');
        if (!query) return;

        this.showLoading(true);

        fetch(`${this.apiBase}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                project: 'chatgpt',
                limit: 5
            })
        })
        .then(response => response.json())
        .then(data => {
            this.showLoading(false);
            this.displaySearchResults(data);
        })
        .catch(error => {
            this.showLoading(false);
            this.showToast('Search failed. Please check connection.', 'error');
        });
    }

    async manualSave() {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            if (!tab || (!tab.url.includes('chat.openai.com') && !tab.url.includes('chatgpt.com'))) {
                this.showToast('Please open ChatGPT to save conversations', 'warning');
                return;
            }

            this.showLoading(true);

            // Send message to content script to save current conversation
            chrome.tabs.sendMessage(tab.id, {
                action: 'manualSave'
            }, (response) => {
                this.showLoading(false);
                
                if (response && response.success) {
                    this.showToast('Conversation saved successfully!', 'success');
                    this.updateStats('autoSaves');
                } else {
                    this.showToast('Failed to save conversation', 'error');
                }
            });

        } catch (error) {
            this.showLoading(false);
            this.showToast('Error saving conversation', 'error');
        }
    }

    displaySearchResults(data) {
        const memories = data.memories || [];
        
        if (memories.length === 0) {
            this.showToast('No memories found for your search', 'info');
            return;
        }

        // Create results display
        const resultsHtml = memories.map((memory, index) => `
            <div style="
                background: rgba(255,255,255,0.1);
                border-radius: 6px;
                padding: 8px;
                margin-bottom: 6px;
                cursor: pointer;
                transition: all 0.2s ease;
            " onclick="navigator.clipboard.writeText('${memory.text.replace(/'/g, "\\'")}')">
                <div style="font-size: 11px; opacity: 0.8; margin-bottom: 4px;">
                    ${memory.memory_type} • ${Math.round(memory.similarity * 100)}% match
                </div>
                <div style="font-size: 12px; line-height: 1.3;">
                    ${memory.text.substring(0, 100)}${memory.text.length > 100 ? '...' : ''}
                </div>
            </div>
        `).join('');

        // Show results in a simple way (since we can't create complex modals in popup)
        alert(`Found ${memories.length} memories:\n\n${memories.map(m => `• ${m.text.substring(0, 60)}...`).join('\n')}\n\nClick any result in ChatGPT to copy it.`);

        this.updateStats('searches');
    }

    async updateStats(type) {
        const current = await chrome.storage.local.get([type]);
        const newValue = (current[type] || 0) + 1;
        
        await chrome.storage.local.set({ [type]: newValue });
        
        if (type === 'autoSaves') {
            document.getElementById('autoSavesCount').textContent = newValue;
        } else if (type === 'searches') {
            document.getElementById('searchesCount').textContent = newValue;
        }
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        const content = document.querySelector('.popup-content');
        
        if (show) {
            loading.style.display = 'block';
            content.style.opacity = '0.5';
        } else {
            loading.style.display = 'none';
            content.style.opacity = '1';
        }
    }

    showToast(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            background: ${type === 'success' ? '#48bb78' : type === 'error' ? '#f56565' : type === 'warning' ? '#ed8936' : '#4299e1'};
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 12px;
            z-index: 10000;
            animation: slideDown 0.3s ease;
        `;
        toast.textContent = message;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideUp 0.3s ease forwards';
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 2000);
    }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PopupController();
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideDown {
        from { transform: translateX(-50%) translateY(-20px); opacity: 0; }
        to { transform: translateX(-50%) translateY(0); opacity: 1; }
    }
    @keyframes slideUp {
        from { transform: translateX(-50%) translateY(0); opacity: 1; }
        to { transform: translateX(-50%) translateY(-20px); opacity: 0; }
    }
`;
document.head.appendChild(style); 
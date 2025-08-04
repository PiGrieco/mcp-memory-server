/**
 * MCP Memory for ChatGPT - Content Script
 * Automatically enhances ChatGPT with persistent memory
 */

class ChatGPTMemoryIntegration {
    constructor() {
        this.apiBase = 'http://localhost:8000';
        this.isActive = false;
        this.messageObserver = null;
        this.memoryUI = null;
        this.sessionId = this.generateSessionId();
        this.userId = 'chatgpt_user';
        
        // Initialize when ready
        this.init();
    }
    
    async init() {
        console.log('🧠 MCP Memory Extension initializing...');
        
        // Wait for ChatGPT to load
        await this.waitForChatGPT();
        
        // Check if API server is running
        const isConnected = await this.checkConnection();
        if (!isConnected) {
            this.showConnectionError();
            return;
        }
        
        // Setup memory integration
        this.setupMemoryUI();
        this.setupMessageInterception();
        this.setupInputEnhancement();
        
        console.log('✅ MCP Memory Extension active!');
        this.isActive = true;
        
        // Show welcome notification
        this.showNotification('🧠 Smart Memory Active!', 'ChatGPT now has persistent memory', 'success');
    }
    
    async waitForChatGPT() {
        return new Promise((resolve) => {
            const checkReady = () => {
                const chatContainer = document.querySelector('[data-testid="conversation-turn"]') ||
                                   document.querySelector('.conversation-content') ||
                                   document.querySelector('main');
                
                if (chatContainer) {
                    resolve();
                } else {
                    setTimeout(checkReady, 1000);
                }
            };
            checkReady();
        });
    }
    
    async checkConnection() {
        try {
            const response = await fetch(`${this.apiBase}/docs`, {
                method: 'GET',
                timeout: 3000
            });
            return response.ok;
        } catch (error) {
            console.warn('MCP Memory API not available:', error);
            return false;
        }
    }
    
    showConnectionError() {
        const errorDiv = document.createElement('div');
        errorDiv.innerHTML = `
            <div style="
                position: fixed;
                top: 20px;
                right: 20px;
                background: #ff4444;
                color: white;
                padding: 15px;
                border-radius: 8px;
                z-index: 10000;
                max-width: 300px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            ">
                <div style="font-weight: bold; margin-bottom: 8px;">
                    🔌 MCP Memory Server Not Found
                </div>
                <div style="font-size: 14px; margin-bottom: 10px;">
                    To enable smart memory, please:
                </div>
                <ol style="font-size: 12px; margin: 0; padding-left: 20px;">
                    <li>Install MCP Memory Server</li>
                    <li>Run: python examples/gpt_smart_auto.py</li>
                    <li>Refresh this page</li>
                </ol>
                <button onclick="this.parentElement.remove()" style="
                    background: white;
                    color: #ff4444;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 4px;
                    margin-top: 10px;
                    cursor: pointer;
                ">Got it</button>
            </div>
        `;
        document.body.appendChild(errorDiv);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (errorDiv.parentElement) {
                errorDiv.remove();
            }
        }, 10000);
    }
    
    setupMemoryUI() {
        // Create floating memory panel
        const memoryPanel = document.createElement('div');
        memoryPanel.id = 'mcp-memory-panel';
        memoryPanel.innerHTML = `
            <div class="memory-header">
                <span class="memory-icon">🧠</span>
                <span class="memory-title">Smart Memory</span>
                <button class="memory-toggle" onclick="this.parentElement.parentElement.classList.toggle('collapsed')">−</button>
            </div>
            <div class="memory-content">
                <div class="memory-stats">
                    <div class="stat">
                        <span class="stat-value" id="auto-saves-count">0</span>
                        <span class="stat-label">Auto-Saves</span>
                    </div>
                    <div class="stat">
                        <span class="stat-value" id="context-retrievals-count">0</span>
                        <span class="stat-label">Context</span>
                    </div>
                </div>
                <div class="memory-actions">
                    <button class="memory-btn" onclick="mcpMemory.showMemorySearch()">
                        🔍 Search Memory
                    </button>
                    <button class="memory-btn" onclick="mcpMemory.toggleAutoMode()">
                        <span id="auto-mode-status">🤖 Auto: ON</span>
                    </button>
                </div>
                <div class="recent-memories" id="recent-memories">
                    <div class="memory-item">Welcome! Memory system is active.</div>
                </div>
            </div>
        `;
        
        document.body.appendChild(memoryPanel);
        this.memoryUI = memoryPanel;
        
        // Make panel draggable
        this.makeDraggable(memoryPanel);
        
        // Add to global scope for button interactions
        window.mcpMemory = this;
    }
    
    makeDraggable(element) {
        let isDragging = false;
        let currentX;
        let currentY;
        let initialX;
        let initialY;
        
        const header = element.querySelector('.memory-header');
        
        header.addEventListener('mousedown', (e) => {
            if (e.target.classList.contains('memory-toggle')) return;
            
            isDragging = true;
            initialX = e.clientX - element.offsetLeft;
            initialY = e.clientY - element.offsetTop;
        });
        
        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            
            e.preventDefault();
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
            
            element.style.left = currentX + 'px';
            element.style.top = currentY + 'px';
        });
        
        document.addEventListener('mouseup', () => {
            isDragging = false;
        });
    }
    
    setupMessageInterception() {
        // Intercept user messages before they're sent
        const inputArea = document.querySelector('textarea[data-id]') || 
                          document.querySelector('textarea[placeholder*="message"]') ||
                          document.querySelector('textarea');
        
        if (inputArea) {
            let lastMessage = '';
            
            // Monitor for message submissions
            const checkForNewMessage = () => {
                const currentValue = inputArea.value;
                
                // If input was cleared (message likely sent)
                if (lastMessage && !currentValue && lastMessage.length > 10) {
                    this.processUserMessage(lastMessage);
                }
                
                lastMessage = currentValue;
            };
            
            // Monitor input changes
            inputArea.addEventListener('input', checkForNewMessage);
            inputArea.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    setTimeout(checkForNewMessage, 100);
                }
            });
        }
        
        // Monitor for ChatGPT responses
        this.setupResponseMonitoring();
    }
    
    setupResponseMonitoring() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // Look for new ChatGPT responses
                        const responses = node.querySelectorAll('[data-message-author-role="assistant"]') ||
                                        node.querySelectorAll('.prose') ||
                                        [];
                        
                        responses.forEach((response) => {
                            if (!response.hasAttribute('data-memory-processed')) {
                                response.setAttribute('data-memory-processed', 'true');
                                this.processChatGPTResponse(response);
                            }
                        });
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    async processUserMessage(message) {
        if (!this.isActive) return;
        
        console.log('📤 Processing user message:', message);
        
        try {
            // Send message to smart memory API
            const response = await fetch(`${this.apiBase}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId,
                    user_id: this.userId
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                
                // Update UI with memory activity
                this.updateMemoryStats(result);
                this.showMemoryActivity(result);
                
                console.log('🧠 Memory processing complete:', result);
            }
        } catch (error) {
            console.error('❌ Memory processing failed:', error);
        }
    }
    
    async processChatGPTResponse(responseElement) {
        if (!this.isActive) return;
        
        const responseText = responseElement.textContent || responseElement.innerText;
        
        // Auto-save important information from ChatGPT responses
        if (this.shouldAutoSave(responseText)) {
            try {
                await fetch(`${this.apiBase}/save`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        text: responseText.substring(0, 500) + (responseText.length > 500 ? '...' : ''),
                        memory_type: 'ai_response',
                        project: 'chatgpt',
                        importance: 0.6
                    })
                });
                
                this.addRecentMemory('💬 AI Response saved');
            } catch (error) {
                console.error('Failed to save AI response:', error);
            }
        }
    }
    
    shouldAutoSave(text) {
        // Save responses that contain useful information
        const savePatterns = [
            /how to/i,
            /step.*by.*step/i,
            /solution/i,
            /explanation/i,
            /code.*example/i,
            /tutorial/i,
            /guide/i
        ];
        
        return savePatterns.some(pattern => pattern.test(text)) && text.length > 100;
    }
    
    updateMemoryStats(result) {
        const autoSavesCount = document.getElementById('auto-saves-count');
        const contextCount = document.getElementById('context-retrievals-count');
        
        if (autoSavesCount && result.auto_saved) {
            const current = parseInt(autoSavesCount.textContent) || 0;
            autoSavesCount.textContent = current + result.auto_saved.length;
        }
        
        if (contextCount && result.context_used) {
            const current = parseInt(contextCount.textContent) || 0;
            contextCount.textContent = current + result.context_used.length;
        }
    }
    
    showMemoryActivity(result) {
        if (result.auto_saved && result.auto_saved.length > 0) {
            this.addRecentMemory(`💾 Auto-saved: ${result.auto_saved.length} items`);
        }
        
        if (result.context_used && result.context_used.length > 0) {
            this.addRecentMemory(`🔍 Retrieved: ${result.context_used.length} memories`);
        }
        
        if (result.proactive_suggestions && result.proactive_suggestions.length > 0) {
            this.addRecentMemory(`💡 Suggestions: ${result.proactive_suggestions.length} found`);
        }
    }
    
    addRecentMemory(text) {
        const recentMemories = document.getElementById('recent-memories');
        if (!recentMemories) return;
        
        const memoryItem = document.createElement('div');
        memoryItem.className = 'memory-item recent';
        memoryItem.textContent = text;
        
        recentMemories.insertBefore(memoryItem, recentMemories.firstChild);
        
        // Keep only last 5 items
        while (recentMemories.children.length > 5) {
            recentMemories.removeChild(recentMemories.lastChild);
        }
        
        // Fade in animation
        setTimeout(() => {
            memoryItem.classList.remove('recent');
        }, 100);
    }
    
    showMemorySearch() {
        const query = prompt('🔍 Search your memory:');
        if (!query) return;
        
        fetch(`${this.apiBase}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                project: 'chatgpt',
                include_analysis: true
            })
        })
        .then(response => response.json())
        .then(result => {
            this.showSearchResults(result);
        })
        .catch(error => {
            console.error('Search failed:', error);
            this.showNotification('❌ Search Failed', 'Could not search memory', 'error');
        });
    }
    
    showSearchResults(result) {
        const memories = result.memories || [];
        
        if (memories.length === 0) {
            this.showNotification('🔍 No Results', 'No memories found for your search', 'info');
            return;
        }
        
        const resultsHtml = memories.map((memory, index) => `
            <div class="search-result" onclick="mcpMemory.copyToClipboard('${memory.text}')">
                <div class="result-header">
                    <span class="result-type">${memory.memory_type}</span>
                    <span class="result-score">${Math.round(memory.similarity * 100)}%</span>
                </div>
                <div class="result-text">${memory.text.substring(0, 150)}...</div>
            </div>
        `).join('');
        
        this.showModal('🔍 Memory Search Results', `
            <div class="search-results">
                ${resultsHtml}
            </div>
            <div class="search-tip">💡 Click any result to copy it</div>
        `);
    }
    
    toggleAutoMode() {
        this.isActive = !this.isActive;
        const statusElement = document.getElementById('auto-mode-status');
        
        if (statusElement) {
            statusElement.textContent = this.isActive ? '🤖 Auto: ON' : '⏸️ Auto: OFF';
        }
        
        this.showNotification(
            this.isActive ? '🤖 Auto Mode ON' : '⏸️ Auto Mode OFF',
            this.isActive ? 'Smart memory is active' : 'Smart memory is paused',
            this.isActive ? 'success' : 'warning'
        );
    }
    
    showNotification(title, message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `memory-notification ${type}`;
        notification.innerHTML = `
            <div class="notification-title">${title}</div>
            <div class="notification-message">${message}</div>
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    showModal(title, content) {
        const modal = document.createElement('div');
        modal.className = 'memory-modal';
        modal.innerHTML = `
            <div class="modal-overlay" onclick="this.parentElement.remove()"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button onclick="this.closest('.memory-modal').remove()">×</button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
    
    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('📋 Copied!', 'Memory copied to clipboard', 'success');
        });
    }
    
    generateSessionId() {
        return 'chatgpt_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    setupInputEnhancement() {
        // Add memory suggestions to input area
        const inputArea = document.querySelector('textarea');
        if (!inputArea) return;
        
        let suggestionTimeout;
        
        inputArea.addEventListener('input', () => {
            clearTimeout(suggestionTimeout);
            suggestionTimeout = setTimeout(() => {
                const text = inputArea.value;
                if (text.length > 20) {
                    this.getSuggestions(text);
                }
            }, 1000);
        });
    }
    
    async getSuggestions(text) {
        try {
            const response = await fetch(`${this.apiBase}/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: text,
                    project: 'chatgpt',
                    limit: 3
                })
            });
            
            const result = await response.json();
            if (result.memories && result.memories.length > 0) {
                this.showInputSuggestions(result.memories);
            }
        } catch (error) {
            // Silently handle suggestion errors
        }
    }
    
    showInputSuggestions(memories) {
        // Remove existing suggestions
        const existing = document.querySelector('.memory-suggestions');
        if (existing) existing.remove();
        
        const suggestions = document.createElement('div');
        suggestions.className = 'memory-suggestions';
        suggestions.innerHTML = `
            <div class="suggestions-header">💡 Related memories:</div>
            ${memories.map(m => `
                <div class="suggestion-item" onclick="mcpMemory.useSuggestion('${m.text}')">
                    ${m.text.substring(0, 80)}...
                </div>
            `).join('')}
        `;
        
        const inputArea = document.querySelector('textarea');
        if (inputArea && inputArea.parentElement) {
            inputArea.parentElement.appendChild(suggestions);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (suggestions.parentElement) {
                    suggestions.remove();
                }
            }, 5000);
        }
    }
    
    useSuggestion(text) {
        const inputArea = document.querySelector('textarea');
        if (inputArea) {
            inputArea.value += '\n\nContext: ' + text;
            inputArea.focus();
        }
        
        // Remove suggestions
        const suggestions = document.querySelector('.memory-suggestions');
        if (suggestions) suggestions.remove();
    }
}

// Initialize when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new ChatGPTMemoryIntegration();
    });
} else {
    new ChatGPTMemoryIntegration();
} 
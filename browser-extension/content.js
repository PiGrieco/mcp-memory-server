/**
 * Production-Ready Content Script for MCP Memory Browser Extension
 * Enhanced with AI platform detection, smart context extraction, and real-time memory suggestions
 */

// Configuration
const CONTENT_CONFIG = {
  PLATFORMS: {
    'chat.openai.com': 'chatgpt',
    'claude.ai': 'claude',
    'poe.com': 'poe',
    'perplexity.ai': 'perplexity',
    'bing.com': 'bing',
    'bard.google.com': 'bard'
  },
  SELECTORS: {
    chatgpt: {
      messages: '[data-message-author-role]',
      input: 'textarea[placeholder*="Message"]',
      sendButton: '[data-testid="send-button"]',
      conversation: '[role="main"]'
    },
    claude: {
      messages: '.claude-message',
      input: 'textarea[placeholder*="Talk to Claude"]',
      sendButton: 'button[type="submit"]',
      conversation: '.conversation-container'
    },
    poe: {
      messages: '.ChatMessage',
      input: 'textarea[class*="textInput"]',
      sendButton: 'button[class*="sendButton"]',
      conversation: '.ChatMessagesView'
    },
    // Add more platforms as needed
    default: {
      messages: '.message, [role="message"], .chat-message',
      input: 'textarea, input[type="text"]',
      sendButton: 'button[type="submit"], .send-button',
      conversation: '.conversation, .chat, main'
    }
  },
  AUTO_SAVE_DELAY: 2000,
  MEMORY_WIDGET_ID: 'mcp-memory-widget',
  SUGGESTION_PANEL_ID: 'mcp-suggestion-panel'
};

// State management
let currentPlatform = 'unknown';
let conversationObserver = null;
let memoryWidget = null;
let suggestionPanel = null;
let lastMessageContent = '';
let autoSaveTimeout = null;
let isInitialized = false;

/**
 * Utility functions
 */
class ContentUtils {
  static detectPlatform() {
    const hostname = window.location.hostname;
    for (const [domain, platform] of Object.entries(CONTENT_CONFIG.PLATFORMS)) {
      if (hostname.includes(domain)) {
        return platform;
      }
    }
    return 'unknown';
  }
  
  static getSelectors(platform = currentPlatform) {
    return CONTENT_CONFIG.SELECTORS[platform] || CONTENT_CONFIG.SELECTORS.default;
  }
  
  static extractTextContent(element) {
    if (!element) return '';
    
    // Remove script and style elements
    const clone = element.cloneNode(true);
    const scripts = clone.querySelectorAll('script, style');
    scripts.forEach(el => el.remove());
    
    return clone.textContent?.trim() || '';
  }
  
  static sanitizeHTML(html) {
    const div = document.createElement('div');
    div.textContent = html;
    return div.innerHTML;
  }
  
  static debounce(func, delay) {
    let timeoutId;
    return (...args) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
  }
  
  static throttle(func, limit) {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }
}

/**
 * Memory extraction and management
 */
class MemoryExtractor {
  static extractConversationContext() {
    const selectors = ContentUtils.getSelectors();
    const conversationElement = document.querySelector(selectors.conversation);
    
    if (!conversationElement) return null;
    
    const messages = Array.from(conversationElement.querySelectorAll(selectors.messages));
    const context = {
      url: window.location.href,
      platform: currentPlatform,
      timestamp: new Date().toISOString(),
      messages: []
    };
    
    messages.forEach((messageEl, index) => {
      const content = ContentUtils.extractTextContent(messageEl);
      if (content.length > 10) { // Filter out very short messages
        const role = this.detectMessageRole(messageEl, index);
        context.messages.push({
          role,
          content: content.substring(0, 2000), // Limit message length
          timestamp: new Date().toISOString(),
          index
        });
      }
    });
    
    return context;
  }
  
  static detectMessageRole(messageEl, index) {
    const content = messageEl.textContent.toLowerCase();
    const classes = messageEl.className.toLowerCase();
    
    // Platform-specific role detection
    if (currentPlatform === 'chatgpt') {
      if (messageEl.getAttribute('data-message-author-role')) {
        return messageEl.getAttribute('data-message-author-role');
      }
    }
    
    // Generic detection
    if (classes.includes('user') || classes.includes('human')) return 'user';
    if (classes.includes('assistant') || classes.includes('ai') || classes.includes('bot')) return 'assistant';
    
    // Fallback: alternate roles
    return index % 2 === 0 ? 'user' : 'assistant';
  }
  
  static async createMemoryFromContext(context, importance = 0.5) {
    if (!context || !context.messages.length) return null;
    
    // Get the last few messages for context
    const recentMessages = context.messages.slice(-6);
    const lastUserMessage = recentMessages.filter(m => m.role === 'user').pop();
    const lastAssistantMessage = recentMessages.filter(m => m.role === 'assistant').pop();
    
    if (!lastUserMessage && !lastAssistantMessage) return null;
    
    // Create memory content
    const memoryContent = this.generateMemoryContent(recentMessages);
    const title = this.generateMemoryTitle(lastUserMessage?.content || lastAssistantMessage?.content);
    
    return {
      content: memoryContent,
      title,
      importance,
      memory_type: 'conversation',
      metadata: {
        platform: currentPlatform,
        url: context.url,
        message_count: recentMessages.length,
        extracted_at: context.timestamp
      },
      project: await this.getCurrentProject()
    };
  }
  
  static generateMemoryContent(messages) {
    const conversationText = messages
      .map(m => `${m.role === 'user' ? 'User' : 'Assistant'}: ${m.content}`)
      .join('\n\n');
    
    return conversationText.substring(0, 5000); // Limit total content
  }
  
  static generateMemoryTitle(content) {
    if (!content) return 'Conversation Memory';
    
    // Extract first meaningful sentence or question
    const sentences = content.split(/[.!?]+/);
    const firstSentence = sentences[0]?.trim();
    
    if (firstSentence && firstSentence.length > 10) {
      return firstSentence.substring(0, 100) + (firstSentence.length > 100 ? '...' : '');
    }
    
    return `Conversation on ${currentPlatform}`;
  }
  
  static async getCurrentProject() {
    try {
      const response = await chrome.runtime.sendMessage({
        type: 'GET_SETTINGS'
      });
      return response.project || 'default';
    } catch (error) {
      console.warn('Failed to get current project:', error);
      return 'default';
    }
  }
}

/**
 * Memory widget for displaying and managing memories
 */
class MemoryWidget {
  constructor() {
    this.element = null;
    this.isVisible = false;
    this.suggestions = [];
  }
  
  async create() {
    if (this.element) return;
    
    this.element = document.createElement('div');
    this.element.id = CONTENT_CONFIG.MEMORY_WIDGET_ID;
    this.element.innerHTML = `
      <div class="mcp-memory-widget">
        <div class="mcp-widget-header">
          <span class="mcp-widget-title">🧠 Memory</span>
          <div class="mcp-widget-controls">
            <button class="mcp-btn mcp-btn-save" title="Save Current Conversation">💾</button>
            <button class="mcp-btn mcp-btn-search" title="Search Memories">🔍</button>
            <button class="mcp-btn mcp-btn-toggle" title="Toggle Panel">📋</button>
            <button class="mcp-btn mcp-btn-close" title="Close Widget">✕</button>
          </div>
        </div>
        <div class="mcp-widget-content" style="display: none;">
          <div class="mcp-memory-stats">
            <span class="mcp-stat-item">Memories: <span id="mcp-memory-count">0</span></span>
            <span class="mcp-stat-item">Suggestions: <span id="mcp-suggestion-count">0</span></span>
          </div>
          <div class="mcp-memory-suggestions" id="mcp-suggestions">
            <!-- Suggestions will be populated here -->
          </div>
          <div class="mcp-memory-actions">
            <input type="text" id="mcp-search-input" placeholder="Search memories..." class="mcp-input">
            <button id="mcp-manual-save" class="mcp-btn mcp-btn-primary">Save Memory</button>
          </div>
        </div>
        <div class="mcp-widget-status">
          <span id="mcp-status-indicator" class="mcp-status-online">●</span>
          <span id="mcp-status-text">Ready</span>
        </div>
      </div>
    `;
    
    // Attach event listeners
    this.attachEventListeners();
    
    // Insert into page
    const targetContainer = this.findBestInsertionPoint();
    if (targetContainer) {
      targetContainer.appendChild(this.element);
    } else {
      document.body.appendChild(this.element);
    }
    
    // Initialize position
    this.positionWidget();
    
    console.log('MCP Memory widget created');
  }
  
  findBestInsertionPoint() {
    const selectors = ContentUtils.getSelectors();
    
    // Try to find a good spot near the conversation
    const candidates = [
      selectors.conversation,
      'main',
      '#app',
      '.app',
      'body'
    ];
    
    for (const selector of candidates) {
      const element = document.querySelector(selector);
      if (element) return element;
    }
    
    return document.body;
  }
  
  positionWidget() {
    if (!this.element) return;
    
    // Position widget in top-right corner
    const style = this.element.style;
    style.position = 'fixed';
    style.top = '20px';
    style.right = '20px';
    style.zIndex = '10000';
    style.maxWidth = '300px';
  }
  
  attachEventListeners() {
    if (!this.element) return;
    
    // Toggle panel
    this.element.querySelector('.mcp-btn-toggle').addEventListener('click', () => {
      this.togglePanel();
    });
    
    // Close widget
    this.element.querySelector('.mcp-btn-close').addEventListener('click', () => {
      this.hide();
    });
    
    // Save memory
    this.element.querySelector('.mcp-btn-save').addEventListener('click', async () => {
      await this.saveCurrentConversation();
    });
    
    // Search memories
    this.element.querySelector('#mcp-search-input').addEventListener('input', 
      ContentUtils.debounce((e) => this.searchMemories(e.target.value), 300)
    );
    
    // Manual save
    this.element.querySelector('#mcp-manual-save').addEventListener('click', async () => {
      await this.saveCurrentConversation(true);
    });
  }
  
  togglePanel() {
    const content = this.element.querySelector('.mcp-widget-content');
    const isVisible = content.style.display !== 'none';
    content.style.display = isVisible ? 'none' : 'block';
    this.isVisible = !isVisible;
  }
  
  async saveCurrentConversation(manual = false) {
    try {
      this.setStatus('Saving...', 'saving');
      
      const context = MemoryExtractor.extractConversationContext();
      if (!context) {
        this.setStatus('No conversation found', 'error');
        return;
      }
      
      const memory = await MemoryExtractor.createMemoryFromContext(
        context, 
        manual ? 0.8 : 0.5 // Higher importance for manual saves
      );
      
      if (!memory) {
        this.setStatus('Nothing to save', 'warning');
        return;
      }
      
      const response = await chrome.runtime.sendMessage({
        type: 'SAVE_MEMORY',
        data: memory
      });
      
      if (response.success) {
        this.setStatus('Memory saved!', 'success');
        this.updateMemoryCount();
      } else {
        this.setStatus('Save failed', 'error');
      }
      
    } catch (error) {
      console.error('Failed to save memory:', error);
      this.setStatus('Save error', 'error');
    }
  }
  
  async searchMemories(query) {
    if (!query.trim()) {
      this.clearSuggestions();
      return;
    }
    
    try {
      const response = await chrome.runtime.sendMessage({
        type: 'SEARCH_MEMORIES',
        data: { query, options: { limit: 5 } }
      });
      
      this.updateSuggestions(response);
      
    } catch (error) {
      console.error('Memory search failed:', error);
    }
  }
  
  updateSuggestions(memories) {
    const container = this.element.querySelector('#mcp-suggestions');
    if (!memories || memories.length === 0) {
      container.innerHTML = '<div class="mcp-no-suggestions">No relevant memories found</div>';
      return;
    }
    
    container.innerHTML = memories.map(memory => `
      <div class="mcp-suggestion-item" data-memory-id="${memory.id}">
        <div class="mcp-suggestion-title">${ContentUtils.sanitizeHTML(memory.title || 'Untitled')}</div>
        <div class="mcp-suggestion-content">${ContentUtils.sanitizeHTML(memory.content.substring(0, 100))}...</div>
        <div class="mcp-suggestion-meta">
          <span class="mcp-suggestion-date">${new Date(memory.created_at).toLocaleDateString()}</span>
          <span class="mcp-suggestion-importance">★${Math.round(memory.importance * 5)}</span>
        </div>
      </div>
    `).join('');
    
    // Add click handlers
    container.querySelectorAll('.mcp-suggestion-item').forEach(item => {
      item.addEventListener('click', () => {
        this.showMemoryDetails(memories.find(m => m.id === item.dataset.memoryId));
      });
    });
    
    this.updateSuggestionCount(memories.length);
  }
  
  clearSuggestions() {
    const container = this.element.querySelector('#mcp-suggestions');
    container.innerHTML = '';
    this.updateSuggestionCount(0);
  }
  
  showMemoryDetails(memory) {
    // Create modal or tooltip with full memory content
    console.log('Showing memory details:', memory);
    // TODO: Implement memory details modal
  }
  
  setStatus(text, type = 'info') {
    const statusText = this.element.querySelector('#mcp-status-text');
    const statusIndicator = this.element.querySelector('#mcp-status-indicator');
    
    statusText.textContent = text;
    statusIndicator.className = `mcp-status-${type}`;
    
    // Auto-clear status after 3 seconds
    setTimeout(() => {
      statusText.textContent = 'Ready';
      statusIndicator.className = 'mcp-status-online';
    }, 3000);
  }
  
  updateMemoryCount(count = null) {
    if (count === null) {
      // Fetch current count
      chrome.runtime.sendMessage({ type: 'GET_STATUS' })
        .then(status => {
          this.element.querySelector('#mcp-memory-count').textContent = status.cacheSize || 0;
        })
        .catch(() => {
          this.element.querySelector('#mcp-memory-count').textContent = '?';
        });
    } else {
      this.element.querySelector('#mcp-memory-count').textContent = count;
    }
  }
  
  updateSuggestionCount(count) {
    this.element.querySelector('#mcp-suggestion-count').textContent = count;
  }
  
  show() {
    if (this.element) {
      this.element.style.display = 'block';
    }
  }
  
  hide() {
    if (this.element) {
      this.element.style.display = 'none';
    }
  }
}

/**
 * Auto-save functionality
 */
class AutoSaveManager {
  static async handleConversationChange() {
    const context = MemoryExtractor.extractConversationContext();
    if (!context || !context.messages.length) return;
    
    const currentContent = context.messages.map(m => m.content).join(' ');
    
    // Check if content has meaningfully changed
    if (this.hasSignificantChange(currentContent, lastMessageContent)) {
      lastMessageContent = currentContent;
      
      // Clear existing timeout
      if (autoSaveTimeout) {
        clearTimeout(autoSaveTimeout);
      }
      
      // Set new timeout for auto-save
      autoSaveTimeout = setTimeout(async () => {
        try {
          const settings = await chrome.runtime.sendMessage({ type: 'GET_SETTINGS' });
          if (settings.autoSave) {
            await memoryWidget.saveCurrentConversation();
          }
        } catch (error) {
          console.warn('Auto-save failed:', error);
        }
      }, CONTENT_CONFIG.AUTO_SAVE_DELAY);
    }
  }
  
  static hasSignificantChange(newContent, oldContent) {
    if (!oldContent) return true;
    
    const lengthDiff = Math.abs(newContent.length - oldContent.length);
    const lengthRatio = lengthDiff / Math.max(newContent.length, oldContent.length);
    
    // Consider significant if content changed by more than 10%
    return lengthRatio > 0.1;
  }
}

/**
 * Conversation monitoring
 */
function setupConversationObserver() {
  const selectors = ContentUtils.getSelectors();
  const conversationElement = document.querySelector(selectors.conversation);
  
  if (!conversationElement) {
    console.warn('Could not find conversation element for platform:', currentPlatform);
    return;
  }
  
  // Clean up existing observer
  if (conversationObserver) {
    conversationObserver.disconnect();
  }
  
  // Create new observer
  conversationObserver = new MutationObserver(
    ContentUtils.throttle(AutoSaveManager.handleConversationChange, 1000)
  );
  
  conversationObserver.observe(conversationElement, {
    childList: true,
    subtree: true,
    characterData: true
  });
  
  console.log('Conversation observer setup for platform:', currentPlatform);
}

/**
 * Message handling
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  const { type, data } = message;
  
  switch (type) {
    case 'RELEVANT_MEMORIES':
      if (memoryWidget) {
        memoryWidget.updateSuggestions(data.memories);
      }
      sendResponse({ success: true });
      break;
      
    case 'PLATFORM_DETECTED':
      currentPlatform = data.platform;
      initialize();
      sendResponse({ success: true });
      break;
      
    default:
      sendResponse({ success: false, error: 'Unknown message type' });
  }
});

/**
 * Initialization
 */
async function initialize() {
  if (isInitialized) return;
  
  try {
    // Detect platform
    currentPlatform = ContentUtils.detectPlatform();
    console.log('MCP Memory initializing for platform:', currentPlatform);
    
    // Wait for page to be ready
    if (document.readyState === 'loading') {
      await new Promise(resolve => {
        document.addEventListener('DOMContentLoaded', resolve, { once: true });
      });
    }
    
    // Additional wait for dynamic content
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Create memory widget
    memoryWidget = new MemoryWidget();
    await memoryWidget.create();
    
    // Setup conversation monitoring
    setupConversationObserver();
    
    // Mark as initialized
    isInitialized = true;
    
    console.log('MCP Memory content script initialized successfully');
    
  } catch (error) {
    console.error('MCP Memory initialization failed:', error);
  }
}

// Auto-initialize when script loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initialize);
} else {
  initialize();
}

// Handle page navigation (for SPAs)
let lastUrl = location.href;
new MutationObserver(() => {
  const currentUrl = location.href;
  if (currentUrl !== lastUrl) {
    lastUrl = currentUrl;
    isInitialized = false;
    setTimeout(initialize, 1000); // Re-initialize after navigation
  }
}).observe(document, { subtree: true, childList: true });

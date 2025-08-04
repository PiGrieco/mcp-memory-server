/**
 * Lovable + MCP Memory Server Integration
 * 
 * This integration allows Lovable's AI to remember context across development sessions
 * Install this as a Lovable plugin or include in your project configuration
 */

class LovableMemoryIntegration {
  constructor(config = {}) {
    this.apiBase = config.apiBase || 'http://localhost:8000';
    this.project = config.project || 'lovable';
    this.enabled = config.enabled !== false;
  }

  /**
   * Save development context to memory
   */
  async saveContext(context) {
    if (!this.enabled) return;

    try {
      const response = await fetch(`${this.apiBase}/save`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: context.description,
          memory_type: context.type || 'development',
          project: this.project,
          importance: context.importance || 0.7,
          tags: context.tags || []
        })
      });

      const result = await response.json();
      console.log('✅ Context saved to memory:', result.message);
      return result;
    } catch (error) {
      console.error('❌ Failed to save context:', error);
    }
  }

  /**
   * Search for relevant development context
   */
  async searchContext(query) {
    if (!this.enabled) return { memories: [] };

    try {
      const response = await fetch(`${this.apiBase}/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          project: this.project,
          limit: 10,
          threshold: 0.3
        })
      });

      const result = await response.json();
      console.log(`🔍 Found ${result.data?.memories?.length || 0} relevant memories`);
      return result.data || { memories: [] };
    } catch (error) {
      console.error('❌ Failed to search context:', error);
      return { memories: [] };
    }
  }

  /**
   * Get project development statistics
   */
  async getProjectStats() {
    if (!this.enabled) return {};

    try {
      const response = await fetch(`${this.apiBase}/stats/${this.project}`);
      const result = await response.json();
      return result.data || {};
    } catch (error) {
      console.error('❌ Failed to get stats:', error);
      return {};
    }
  }

  /**
   * Hook into Lovable's development workflow
   */
  setupLovableHooks() {
    // Hook into file changes
    if (typeof window !== 'undefined' && window.lovable) {
      window.lovable.onFileChange = async (file, changes) => {
        await this.saveContext({
          description: `File ${file.name} modified: ${changes.summary}`,
          type: 'file_change',
          importance: 0.6,
          tags: ['file_change', file.extension, 'modification']
        });
      };

      // Hook into component creation
      window.lovable.onComponentCreate = async (component) => {
        await this.saveContext({
          description: `Created component ${component.name}: ${component.description}`,
          type: 'component',
          importance: 0.8,
          tags: ['component', 'creation', component.framework]
        });
      };

      // Hook into bug fixes
      window.lovable.onBugFix = async (bug) => {
        await this.saveContext({
          description: `Fixed bug: ${bug.description}. Solution: ${bug.solution}`,
          type: 'bug_fix',
          importance: 0.9,
          tags: ['bug_fix', 'solution', bug.category]
        });
      };
    }
  }
}

// Lovable Plugin Configuration
const memoryConfig = {
  name: 'MCP Memory Server',
  version: '1.0.0',
  description: 'Persistent memory for AI development context',
  
  // Plugin initialization
  async initialize(lovable) {
    console.log('🧠 Initializing MCP Memory Server integration...');
    
    const memory = new LovableMemoryIntegration({
      project: lovable.project.name || 'lovable',
      enabled: true
    });

    // Setup hooks
    memory.setupLovableHooks();

    // Add memory methods to Lovable context
    lovable.memory = {
      save: (text, type = 'note') => memory.saveContext({
        description: text,
        type: type,
        importance: 0.7
      }),
      search: (query) => memory.searchContext(query),
      stats: () => memory.getProjectStats()
    };

    // Add AI prompt enhancement
    const originalPrompt = lovable.ai.generatePrompt;
    lovable.ai.generatePrompt = async function(task) {
      // Search for relevant context
      const relevantMemories = await memory.searchContext(task.description);
      
      // Enhance prompt with memory context
      let enhancedPrompt = await originalPrompt.call(this, task);
      
      if (relevantMemories.memories && relevantMemories.memories.length > 0) {
        enhancedPrompt += '\n\n## Relevant Context from Memory:\n';
        relevantMemories.memories.forEach((mem, i) => {
          enhancedPrompt += `${i + 1}. ${mem.text} (${mem.memory_type})\n`;
        });
      }
      
      return enhancedPrompt;
    };

    console.log('✅ MCP Memory Server integration active');
    return memory;
  }
};

// Export for Lovable
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { LovableMemoryIntegration, memoryConfig };
}

// Browser global
if (typeof window !== 'undefined') {
  window.LovableMemoryIntegration = LovableMemoryIntegration;
} 
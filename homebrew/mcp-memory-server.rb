class McpMemoryServer < Formula
  desc "The Redis for AI Agents - Persistent memory system for any AI assistant"
  homepage "https://github.com/AiGotsrl/mcp-memory-server"
  url "https://github.com/AiGotsrl/mcp-memory-server/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "PUT_SHA256_HERE"
  license "MIT"
  head "https://github.com/AiGotsrl/mcp-memory-server.git", branch: "main"

  depends_on "python@3.11"
  depends_on "docker" => :optional
  depends_on "mongodb-community" => :optional
  depends_on "node" => :optional

  resource "sentence-transformers" do
    url "https://files.pythonhosted.org/packages/sentence-transformers-2.2.2.tar.gz"
    sha256 "PUT_SENTENCE_TRANSFORMERS_SHA256_HERE"
  end

  def install
    # Install Python dependencies
    venv = virtualenv_create(libexec, "python3.11")
    
    # Core dependencies
    venv.pip_install "pymongo>=4.5.0"
    venv.pip_install "motor>=3.3.0" 
    venv.pip_install "sentence-transformers>=2.2.0"
    venv.pip_install "fastapi>=0.100.0"
    venv.pip_install "uvicorn>=0.23.0"
    venv.pip_install "pydantic>=2.0.0"
    venv.pip_install "numpy>=1.24.0"
    venv.pip_install "aiofiles>=23.1.0"
    venv.pip_install "python-dateutil>=2.8.2"
    venv.pip_install "regex>=2023.6.3"
    venv.pip_install "pandas>=2.0.0"
    venv.pip_install "scikit-learn>=1.3.0"
    
    # CLI dependencies
    venv.pip_install "click>=8.0.0"
    venv.pip_install "rich>=13.0.0"
    venv.pip_install "inquirer>=3.1.0"
    venv.pip_install "pyyaml>=6.0"
    venv.pip_install "requests>=2.31.0"
    venv.pip_install "colorama>=0.4.6"
    
    # Install the package
    venv.pip_install_and_link buildpath

    # Create bin scripts
    (bin/"mcp-memory").write <<~EOS
      #!/bin/bash
      exec "#{libexec}/bin/python" -m mcp_memory.cli "$@"
    EOS
    
    (bin/"mcp-memory-server").write <<~EOS
      #!/bin/bash
      exec "#{libexec}/bin/python" -m mcp_memory.server "$@"
    EOS
    
    (bin/"mcp-memory-setup").write <<~EOS
      #!/bin/bash
      exec "#{libexec}/bin/python" -m mcp_memory.setup.wizard "$@"
    EOS

    # Make scripts executable
    chmod "+x", bin/"mcp-memory"
    chmod "+x", bin/"mcp-memory-server" 
    chmod "+x", bin/"mcp-memory-setup"

    # Install configuration templates
    (prefix/"share/mcp-memory").mkpath
    cp_r "config", prefix/"share/mcp-memory"
    cp_r "examples", prefix/"share/mcp-memory"
    cp_r "templates", prefix/"share/mcp-memory" if File.exist?("templates")

    # Install documentation
    (doc).mkpath
    cp "README.md", doc
    cp "SMART_AUTOMATION_GUIDE.md", doc if File.exist?("SMART_AUTOMATION_GUIDE.md")
    cp "PLUGIN_ECOSYSTEM.md", doc if File.exist?("PLUGIN_ECOSYSTEM.md")
    cp "LICENSE", doc if File.exist?("LICENSE")
  end

  def post_install
    # Create config directory
    (var/"mcp-memory").mkpath
    
    # Set up initial configuration if it doesn't exist
    config_file = var/"mcp-memory/config.yaml"
    unless config_file.exist?
      config_file.write <<~EOS
        # MCP Memory Server Configuration
        mongodb:
          url: "mongodb://localhost:27017"
          database: "memory_db"
          
        embedding:
          model: "sentence-transformers/all-MiniLM-L6-v2"
          
        api:
          host: "localhost"
          port: 8000
          
        logging:
          level: "INFO"
      EOS
    end

    puts <<~EOS
      🧠 MCP Memory Server installed successfully!
      
      Quick Start:
        # Interactive setup for all AI tools
        mcp-memory-setup
        
        # Setup specific tools
        mcp-memory --setup-claude
        mcp-memory --setup-gpt
        mcp-memory --setup-cursor
        
        # Start the server
        mcp-memory-server
      
      Configuration: #{var}/mcp-memory/config.yaml
      Documentation: #{doc}
      Examples: #{prefix}/share/mcp-memory/examples
      
      Next steps:
      1. Run 'mcp-memory-setup' for guided installation
      2. Visit https://github.com/AiGotsrl/mcp-memory-server for docs
      
      Transform your AI tools into super-intelligent assistants! 🚀
    EOS
  end

  def caveats
    <<~EOS
      🔧 Additional Setup:
      
      For optimal experience:
      • Install Docker: brew install --cask docker
      • Install MongoDB: brew install mongodb-community
      • Install Node.js: brew install node (for Lovable integration)
      
      AI Tool Integration:
      • Claude Desktop: Auto-detected and configured
      • ChatGPT: Browser extension available 
      • Cursor: VS Code marketplace extension
      • Lovable: JavaScript plugin
      • Replit: Template integration
      
      Run 'mcp-memory-setup' for interactive configuration!
    EOS
  end

  test do
    # Test Python import
    system libexec/"bin/python", "-c", "import mcp_memory; print('Import successful')"
    
    # Test CLI
    output = shell_output("#{bin}/mcp-memory --version")
    assert_match "1.0.0", output
    
    # Test configuration
    system bin/"mcp-memory", "--check-config"
  end
end 
#!/usr/bin/env python3
"""
MCP Memory Server - Setup configuration for PyPI publication
The Redis for AI Agents - Persistent memory for any AI assistant
"""

from setuptools import setup, find_packages
import os
import sys
from pathlib import Path

# Ensure we're using Python 3.11+
if sys.version_info < (3, 11):
    sys.exit("Python 3.11+ is required for MCP Memory Server")

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "MCP Memory Server - Persistent memory system for AI agents"

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Additional CLI-specific requirements
cli_requirements = [
    "click>=8.0.0",
    "rich>=13.0.0", 
    "inquirer>=3.1.0",
    "pyyaml>=6.0",
    "requests>=2.31.0",
    "colorama>=0.4.6",
    "progress>=1.6",
    "psutil>=5.9.0",
]

# Development requirements
dev_requirements = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.7.0",
    "flake8>=6.0.0",
    "mypy>=1.5.0",
    "isort>=5.12.0",
    "pre-commit>=3.3.0",
    "bandit[toml]>=1.7.5",
]

setup(
    name="mcp-memory-server",
    version="1.0.0",
    description="The Redis for AI Agents - Persistent memory system for any AI assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AiGot Srl",
    author_email="support@mcp-memory.ai",
    url="https://github.com/AiGotsrl/mcp-memory-server",
    project_urls={
        "Bug Reports": "https://github.com/AiGotsrl/mcp-memory-server/issues",
        "Source": "https://github.com/AiGotsrl/mcp-memory-server",
        "Documentation": "https://github.com/AiGotsrl/mcp-memory-server/blob/main/SMART_AUTOMATION_GUIDE.md",
        "Plugin Ecosystem": "https://github.com/AiGotsrl/mcp-memory-server/blob/main/PLUGIN_ECOSYSTEM.md",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "mcp_memory": [
            "templates/*",
            "config/*",
            "examples/*",
        ]
    },
    python_requires=">=3.11",
    install_requires=requirements + cli_requirements,
    extras_require={
        "dev": dev_requirements,
        "all": dev_requirements + cli_requirements,
        "claude": ["anthropic>=0.3.0"],
        "openai": ["openai>=1.3.0"],
        "browser": ["selenium>=4.15.0", "webdriver-manager>=4.0.0"],
        "cloud": ["boto3>=1.29.0", "azure-storage-blob>=12.19.0"],
    },
    entry_points={
        "console_scripts": [
            # Main CLI command
            "mcp-memory=mcp_memory.cli:main",
            
            # Setup commands (user-friendly)
            "mcp-memory-setup=mcp_memory.setup.wizard:main",
            "mcp-memory-setup-all=mcp_memory.setup.all_tools:main",
            "mcp-memory-setup-claude=mcp_memory.setup.claude:main",
            "mcp-memory-setup-gpt=mcp_memory.setup.gpt:main",
            "mcp-memory-setup-cursor=mcp_memory.setup.cursor:main",
            "mcp-memory-setup-lovable=mcp_memory.setup.lovable:main",
            "mcp-memory-setup-replit=mcp_memory.setup.replit:main",
            
            # Server commands
            "mcp-memory-server=mcp_memory.server:main",
            "mcp-memory-api=mcp_memory.api.server:main",
            
            # Utility commands
            "mcp-memory-doctor=mcp_memory.utils.doctor:main",
            "mcp-memory-migrate=mcp_memory.utils.migrate:main",
            "mcp-memory-export=mcp_memory.utils.export:main",
            "mcp-memory-import=mcp_memory.utils.import_data:main",
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop", 
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: System :: Distributed Computing",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Text Processing :: Linguistic",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Framework :: AsyncIO",
        "Typing :: Typed",
    ],
    keywords=[
        "ai", "artificial-intelligence", "memory", "mcp", "chatgpt", "claude", 
        "cursor", "lovable", "replit", "automation", "machine-learning", 
        "embedding", "vector-search", "smart-assistant", "persistent-memory",
        "semantic-search", "mongodb", "docker", "fastapi", "anthropic", "openai"
    ],
    license="MIT",
    platforms=["any"],
    zip_safe=False,
    # Security
    options={
        "bdist_wheel": {
            "universal": False,
        }
    },
) 
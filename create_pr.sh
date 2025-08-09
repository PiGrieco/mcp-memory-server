#!/bin/bash

# MCP Memory Server v2.0.0 - Production Ready PR Creation Script

echo "🚀 Creating Production Ready PR for MCP Memory Server v2.0.0"
echo "============================================================"

# Repository information
REPO_URL="https://github.com/AiGotsrl/mcp-memory-server"
PR_BRANCH="production-ready-v2"
BASE_BRANCH="main"

# PR Details
PR_TITLE="🎉 MCP Memory Server v2.0.0 - Production Ready Release"
PR_LABELS="enhancement,major-release,production-ready,breaking-change"

echo "📋 PR Information:"
echo "  Repository: $REPO_URL"
echo "  Branch: $PR_BRANCH -> $BASE_BRANCH"
echo "  Title: $PR_TITLE"
echo ""

# Create the PR URL with pre-filled information
PR_URL="${REPO_URL}/compare/${BASE_BRANCH}...${PR_BRANCH}?quick_pull=1"

echo "🔗 PR Creation URL:"
echo "$PR_URL"
echo ""

echo "📝 PR Description (copy from PR_DESCRIPTION.md):"
echo "   File: $(pwd)/PR_DESCRIPTION.md"
echo ""

echo "📋 Quick Setup Instructions:"
echo "1. Open the PR URL above in your browser"
echo "2. Copy the content from PR_DESCRIPTION.md into the PR description"
echo "3. Add the following labels:"
echo "   - enhancement"
echo "   - major-release" 
echo "   - production-ready"
echo "   - breaking-change"
echo "4. Request reviews from:"
echo "   - @architecture-team"
echo "   - @security-team"
echo "   - @frontend-team"
echo "   - @integrations-team"
echo ""

echo "🎯 Key Points to Highlight:"
echo "✅ Complete merge of main and dev branches"
echo "✅ Production-ready architecture with 95% test coverage"
echo "✅ Enhanced cloud infrastructure with MongoDB Atlas"
echo "✅ Modern browser extension with multi-platform support"
echo "✅ Unified AI integrations (Cursor, Claude, GPT)"
echo "✅ New React dashboard with real-time monitoring"
echo "✅ Comprehensive documentation and migration guides"
echo ""

echo "⚠️  Breaking Changes Note:"
echo "This is a major release with breaking changes."
echo "Migration path is provided and tested."
echo ""

echo "🚀 Opening PR URL..."
if command -v open >/dev/null 2>&1; then
    open "$PR_URL"
    echo "✅ PR URL opened in browser"
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$PR_URL"
    echo "✅ PR URL opened in browser"
else
    echo "Please manually open: $PR_URL"
fi

echo ""
echo "📄 Don't forget to copy the PR description from:"
echo "   $(pwd)/PR_DESCRIPTION.md"
echo ""
echo "🎉 Ready to create the Production Ready PR!"

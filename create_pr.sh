#!/bin/bash
# Script to create GitHub PR for Auto-Trigger Edition

echo "🚀 Creating GitHub PR for MCP Memory Server v2.0 Auto-Trigger Edition"
echo "========================================================================="

# Get repository info
REPO_URL=$(git remote get-url origin)
REPO_NAME=$(basename "$REPO_URL" .git)
REPO_OWNER=$(basename $(dirname "$REPO_URL"))

echo "📁 Repository: $REPO_OWNER/$REPO_NAME"
echo "🌿 Branch: production-ready-v2"
echo "🎯 Target: main"

# Check if GitHub CLI is available
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI found, creating PR automatically..."
    
    # Create PR with GitHub CLI
    gh pr create \
        --title "🚀 MCP Memory Server v2.0 - Auto-Trigger Edition" \
        --body-file PR_AUTO_TRIGGER_V2.md \
        --base main \
        --head production-ready-v2 \
        --label "enhancement,auto-trigger,v2.0" \
        --assignee "@me"
    
    echo "✅ PR created successfully!"
    echo "🔗 Opening PR in browser..."
    gh pr view --web
    
else
    echo "⚠️  GitHub CLI not found, providing manual instructions..."
    echo ""
    echo "📋 MANUAL PR CREATION:"
    echo "1. Go to: https://github.com/$REPO_OWNER/$REPO_NAME/compare/main...production-ready-v2"
    echo "2. Title: 🚀 MCP Memory Server v2.0 - Auto-Trigger Edition"
    echo "3. Copy description from: PR_AUTO_TRIGGER_V2.md"
    echo "4. Add labels: enhancement, auto-trigger, v2.0"
    echo "5. Request review from team members"
    echo ""
    echo "🔗 Direct link:"
    echo "https://github.com/$REPO_OWNER/$REPO_NAME/compare/main...production-ready-v2"
    echo ""
    
    # Try to open in browser (macOS)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "🌐 Opening in browser..."
        open "https://github.com/$REPO_OWNER/$REPO_NAME/compare/main...production-ready-v2"
    fi
fi

echo ""
echo "📋 PR DESCRIPTION SUMMARY:"
echo "• Revolutionary 7-type auto-trigger system"
echo "• One-click installation (2 minutes vs 30-60 minutes)"
echo "• Zero external dependencies required"
echo "• Universal AI platform compatibility"
echo "• Complete documentation rewrite"
echo "• 23 new files added"
echo "• Backwards compatible"
echo ""
echo "🎯 KEY FEATURES TO HIGHLIGHT IN REVIEW:"
echo "• Auto-trigger on keywords: 'ricorda', 'importante', 'risolto'"
echo "• Semantic similarity search for context"
echo "• Pattern recognition for solutions"
echo "• Automatic Cursor/Claude configuration"
echo "• Comprehensive testing suite"
echo ""
echo "✅ Ready for review and merge!"
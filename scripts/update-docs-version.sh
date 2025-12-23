#!/bin/bash
set -e

# Script to manually update version numbers in documentation
# Usage: ./scripts/update-docs-version.sh [version]
#   If version not provided, reads from VERSION file

VERSION_FILE="VERSION"

if [ -z "$1" ]; then
    if [ ! -f "$VERSION_FILE" ]; then
        echo "❌ ERROR: VERSION file not found and no version argument provided"
        echo "Usage: $0 [version]"
        exit 1
    fi
    VERSION=$(cat "$VERSION_FILE" | tr -d '[:space:]')
    echo "📖 Reading version from VERSION file: $VERSION"
else
    VERSION="$1"
    echo "📝 Using provided version: $VERSION"
fi

echo ""
echo "🔄 Updating documentation to version $VERSION..."
echo ""

# Backup files
echo "📦 Creating backups..."
cp AGENTS.md AGENTS.md.bak
cp ARCHITECTURE.md ARCHITECTURE.md.bak

# Update AGENTS.md
echo "✏️  Updating AGENTS.md..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/\*\*Version\*\*: .*/\*\*Version**: $VERSION/" AGENTS.md
else
    # Linux
    sed -i "s/\*\*Version\*\*: .*/\*\*Version**: $VERSION/" AGENTS.md
fi

# Update ARCHITECTURE.md
echo "✏️  Updating ARCHITECTURE.md..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/\*\*Version\*\*: .*/\*\*Version**: $VERSION/" ARCHITECTURE.md
else
    # Linux
    sed -i "s/\*\*Version\*\*: .*/\*\*Version**: $VERSION/" ARCHITECTURE.md
fi

# Verify changes
echo ""
echo "✅ Documentation updated successfully!"
echo ""
echo "📋 Changes:"
echo "   AGENTS.md: $(grep '\*\*Version\*\*:' AGENTS.md)"
echo "   ARCHITECTURE.md: $(grep '\*\*Version\*\*:' ARCHITECTURE.md)"
echo ""

# Remove backups
rm -f AGENTS.md.bak ARCHITECTURE.md.bak

echo "💡 Tip: Run 'git diff' to review changes"

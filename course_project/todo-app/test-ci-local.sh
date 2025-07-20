#!/bin/bash

# Install Act (if not already installed)
# macOS: brew install act
# Linux: curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

echo "=== Running CI/CD Pipeline Locally with Act ==="
echo ""

# Check if act is installed
if ! command -v act &> /dev/null; then
    echo "❌ Act is not installed. Install it first:"
    echo "   macOS: brew install act"
    echo "   Linux: curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash"
    exit 1
fi

echo "✅ Act is installed"
echo ""

# List available jobs
echo "📋 Available GitHub Actions jobs:"
act --list
echo ""

# Run individual jobs
echo "🔄 You can run individual jobs:"
echo "   act --job test-unit           # Run unit tests"
echo "   act --job test-integration    # Run integration tests"
echo "   act --job test-container      # Run container tests (requires Docker)"
echo ""

echo "🚀 Running all jobs:"
act

echo ""
echo "✅ Local CI/CD pipeline completed!"
echo ""
echo "💡 Tips:"
echo "   - Use 'act --verbose' for detailed output"
echo "   - Use 'act --dry-run' to see what would run"
echo "   - Container tests require Docker to be running"

#!/bin/bash
# Fix Hugging Face cache permission issues

echo "🔧 Fixing Hugging Face cache permissions..."

# Remove lock files
echo "Removing lock files..."
find ~/.cache/huggingface -name "*.lock" -delete 2>/dev/null

# Fix permissions
echo "Fixing permissions..."
chmod -R u+w ~/.cache/huggingface 2>/dev/null

# Create cache directory if it doesn't exist
mkdir -p ~/.cache/huggingface/hub

echo "✅ Cache fixed! Try running the server again."

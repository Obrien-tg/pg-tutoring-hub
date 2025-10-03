#!/bin/bash
# GitHub Setup Commands for PG Tutoring Hub
# Replace YOUR_GITHUB_USERNAME and YOUR_REPO_NAME with actual values

echo "🔗 Setting up GitHub remote repository..."

# Add the remote repository (replace with your actual GitHub repo URL)
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git

# Set the main branch name
git branch -M main

# Push master branch
echo "📤 Pushing master branch..."
git push -u origin main

# Push development branch
echo "📤 Pushing development branch..."
git checkout development
git push -u origin development

# Push feature branches
echo "📤 Pushing feature branches..."
git push -u origin feature/chat-system
git push -u origin feature/ui-enhancements  
git push -u origin feature/assignments-system

# Set development as default branch for development work
git checkout development

echo "✅ Successfully pushed all branches to GitHub!"
echo "🌐 Your repository is now available at: https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME"
echo "🌳 Branches created:"
echo "   - main (production)"
echo "   - development (default for development)"
echo "   - feature/chat-system"
echo "   - feature/ui-enhancements"
echo "   - feature/assignments-system"
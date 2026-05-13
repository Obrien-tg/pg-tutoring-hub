#!/bin/bash
# PG Tutoring Hub - GitHub Repository Setup

echo "🚀 Setting up PG Tutoring Hub on GitHub..."
echo ""
echo "📋 STEPS TO COMPLETE GITHUB SETUP:"
echo ""
echo "1. 🌐 Go to https://github.com and sign in"
echo "2. ➕ Click the '+' icon → 'New repository'"
echo "3. 📝 Repository details:"
echo "   - Name: pg-tutoring-hub"
echo "   - Description: Professional tutoring platform for Patience Gwanyanya - Django web application"
echo "   - Visibility: Choose Public or Private"
echo "   - ❌ DO NOT add README, .gitignore, or license (we have them)"
echo "4. ✅ Click 'Create repository'"
echo ""
echo "5. 🔄 After creating the repo, run this script again with 'push' parameter:"
echo "   ./scripts/create_and_push.sh push"
echo ""

if [ "$1" = "push" ]; then
    echo "📤 Pushing all branches to GitHub..."
    
    # Push main branch
    echo "📤 Pushing main branch..."
    git checkout main
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
    
    # Set development as default working branch
    git checkout development
    
    echo ""
    echo "🎉 SUCCESS! All branches pushed to GitHub!"
    echo ""
    echo "🌐 Repository URL: https://github.com/obrien-tg/pg-tutoring-hub"
    echo ""
    echo "🌳 Branches created on GitHub:"
    echo "   ✅ main (production)"
    echo "   ✅ development (default for development work)"
    echo "   ✅ feature/chat-system"
    echo "   ✅ feature/ui-enhancements"
    echo "   ✅ feature/assignments-system"
    echo ""
    echo "💡 Next steps:"
    echo "   - Set up branch protection rules on GitHub"
    echo "   - Configure GitHub Pages (if needed)"
    echo "   - Set up CI/CD workflows"
    echo "   - Invite collaborators"
    
else
    echo "💡 After creating the GitHub repository, run:"
    echo "   ./scripts/create_and_push.sh push"
fi
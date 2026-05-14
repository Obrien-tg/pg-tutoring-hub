#!/bin/bash
# PG Tutoring Hub - Development Workflow Helper

show_help() {
    echo "🚀 PG Tutoring Hub - Development Workflow Helper"
    echo ""
    echo "Usage: ./dev-workflow.sh [command]"
    echo ""
    echo "Commands:"
    echo "  new-feature <name>    Create a new feature branch"
    echo "  switch <branch>       Switch to a branch"
    echo "  sync                  Sync with development branch"
    echo "  status               Show current branch and status"
    echo "  push                 Push current branch to remote"
    echo "  list                 List all branches"
    echo "  clean                Clean up merged feature branches"
    echo ""
    echo "Examples:"
    echo "  ./dev-workflow.sh new-feature user-profiles"
    echo "  ./dev-workflow.sh switch development"
    echo "  ./dev-workflow.sh sync"
}

new_feature() {
    if [ -z "$1" ]; then
        echo "❌ Error: Feature name required"
        echo "Usage: ./dev-workflow.sh new-feature <name>"
        exit 1
    fi
    
    echo "🌿 Creating new feature branch: feature/$1"
    git checkout development
    git pull origin development
    git checkout -b "feature/$1"
    echo "✅ Created and switched to feature/$1"
    echo "💡 Start developing and commit your changes!"
}

switch_branch() {
    if [ -z "$1" ]; then
        echo "❌ Error: Branch name required"
        echo "Usage: ./dev-workflow.sh switch <branch>"
        exit 1
    fi
    
    echo "🔄 Switching to branch: $1"
    git checkout "$1"
    echo "✅ Switched to $1"
}

sync_development() {
    echo "🔄 Syncing with development branch..."
    current_branch=$(git branch --show-current)
    git checkout development
    git pull origin development
    
    if [ "$current_branch" != "development" ]; then
        echo "🔄 Switching back to $current_branch and rebasing..."
        git checkout "$current_branch"
        git rebase development
        echo "✅ Rebased $current_branch with latest development"
    fi
}

show_status() {
    echo "📊 Current Repository Status"
    echo "=========================="
    echo "Current branch: $(git branch --show-current)"
    echo ""
    echo "📈 Git Status:"
    git status --short
    echo ""
    echo "🌳 Recent commits:"
    git log --oneline -5
}

push_current() {
    current_branch=$(git branch --show-current)
    echo "📤 Pushing $current_branch to remote..."
    git push -u origin "$current_branch"
    echo "✅ Pushed $current_branch to GitHub"
}

list_branches() {
    echo "🌳 All Branches:"
    git branch -a
    echo ""
    echo "📊 Branch status:"
    echo "  * = current branch"
    echo "  remotes/origin/ = remote branches"
}

clean_branches() {
    echo "🧹 Cleaning up merged feature branches..."
    git checkout development
    git branch --merged | grep "feature/" | xargs -n 1 git branch -d
    echo "✅ Cleaned up local merged feature branches"
    echo "💡 To clean remote branches, use: git remote prune origin"
}

# Main command dispatcher
case "$1" in
    "new-feature")
        new_feature "$2"
        ;;
    "switch")
        switch_branch "$2"
        ;;
    "sync")
        sync_development
        ;;
    "status")
        show_status
        ;;
    "push")
        push_current
        ;;
    "list")
        list_branches
        ;;
    "clean")
        clean_branches
        ;;
    *)
        show_help
        ;;
esac
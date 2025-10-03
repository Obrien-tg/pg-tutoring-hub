# PG Tutoring Hub - Git Branching Strategy

## 🌳 Branch Structure

### Main Branches

#### `master` (Production)
- **Purpose**: Production-ready code
- **Protection**: Protected branch, no direct commits
- **Deployment**: Automatic deployment to production server
- **Merges from**: `development` branch only (via pull requests)

#### `development` (Integration)
- **Purpose**: Integration branch for all features
- **Protection**: Semi-protected, requires pull request reviews
- **Testing**: Staging environment deployment
- **Merges from**: Feature branches
- **Merges to**: `master` branch

### Feature Branches

#### `feature/chat-system`
- **Purpose**: Real-time chat functionality development
- **Tasks**:
  - WebSocket integration with Django Channels
  - Chat room management
  - Message persistence and history
  - Real-time notifications

#### `feature/ui-enhancements`
- **Purpose**: User interface and experience improvements
- **Tasks**:
  - Advanced animations and transitions
  - Mobile responsiveness enhancements
  - Accessibility improvements
  - Custom theme development

#### `feature/assignments-system`
- **Purpose**: Advanced assignment and grading system
- **Tasks**:
  - Assignment submission system
  - Grading and feedback tools
  - Progress analytics
  - Due date notifications

## 🔄 Workflow Process

### 1. Feature Development
```bash
# Start new feature
git checkout development
git pull origin development
git checkout -b feature/new-feature-name

# Work on feature
git add .
git commit -m "Add feature implementation"

# Push to remote
git push origin feature/new-feature-name
```

### 2. Feature Integration
```bash
# Create pull request: feature/new-feature → development
# After review and approval, merge via GitHub
# Delete feature branch after merge
```

### 3. Release Process
```bash
# Create pull request: development → master
# After thorough testing and review, merge via GitHub
# Tag release version
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## 🛡️ Branch Protection Rules

### Master Branch
- Require pull request reviews before merging
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Restrict pushes that create files larger than 100MB
- Require linear history

### Development Branch
- Require pull request reviews before merging
- Require status checks to pass before merging
- Allow force pushes (for maintainers only)

## 🏷️ Commit Message Convention

### Format
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

### Examples
```bash
feat(chat): add real-time messaging system
fix(auth): resolve login redirect issue
docs(readme): update installation instructions
style(dashboard): improve responsive layout
refactor(models): optimize database queries
test(users): add registration form tests
chore(deps): update Django to 5.2.7
```

## 📝 Pull Request Template

When creating pull requests, include:

1. **Description**: What does this PR do?
2. **Type of Change**: Bug fix, new feature, breaking change, etc.
3. **Testing**: How has this been tested?
4. **Screenshots**: UI changes (if applicable)
5. **Checklist**:
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Tests added/updated
   - [ ] Documentation updated

## 🚀 Environment Mapping

- **`master`** → Production Server
- **`development`** → Staging Server  
- **Feature branches** → Local development

## 📊 Release Schedule

- **Patch releases**: As needed (bug fixes)
- **Minor releases**: Bi-weekly (new features)
- **Major releases**: Monthly (significant updates)

---

*This branching strategy ensures code quality, proper testing, and smooth deployments for the PG Tutoring Hub platform.*
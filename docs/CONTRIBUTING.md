# Contributing Guidelines

Thank you for your interest in contributing to Recipe Recommender! This document provides comprehensive guidelines for contributing to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style and Standards](#code-style-and-standards)
- [Development Workflow](#development-workflow)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Standards](#documentation-standards)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Security Guidelines](#security-guidelines)
- [Community Guidelines](#community-guidelines)

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Python 3.11+** with `uv` package manager
- **Node.js 18+** with npm
- **Git** for version control
- **Docker** (optional, for containerized development)
- Basic understanding of Flask, React, and machine learning concepts

### First-Time Setup

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/recipe-recommender.git
   cd recipe-recommender
   ```

2. **Add Upstream Remote**
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/recipe-recommender.git
   ```

3. **Install Dependencies**
   ```bash
   # Python dependencies
   uv sync

   # Frontend dependencies
   cd food-recipe-recommender/app/frontend
   npm install
   cd ../../..
   ```

4. **Set Up Environment**
   ```bash
   cp food-recipe-recommender/app/.env.example food-recipe-recommender/app/.env
   # Edit .env with your development settings
   ```

5. **Verify Setup**
   ```bash
   # Run tests to ensure everything works
   make test
   make test-frontend
   ```

## Development Setup

### Local Development Environment

#### Backend Development

```bash
# Start Flask development server
cd food-recipe-recommender/app
uv run flask --app app:create_app run --debug --port 8080
```

**Key Features:**
- Auto-reload on code changes
- Debug mode with detailed error messages
- SQLite database for development
- Mock email services in development mode

#### Frontend Development

```bash
# Start Vite development server
cd food-recipe-recommender/app/frontend
npm run dev
```

**Key Features:**
- Hot module replacement (HMR)
- Proxy to backend API
- TypeScript compilation
- ESLint integration

#### Full-Stack Development

```bash
# Terminal 1: Backend
cd food-recipe-recommender/app
uv run flask --app app:create_app run --debug --port 8080

# Terminal 2: Frontend
cd food-recipe-recommender/app/frontend
npm run dev

# Access application at http://localhost:5173
```

### Docker Development

```bash
# Build development image
docker build -t recipe-recommender-dev .

# Run with development settings
docker run -p 8080:8080 \
  -v $(pwd):/app \
  -e ENV=development \
  recipe-recommender-dev
```

### IDE Configuration

#### VS Code Setup

**Recommended Extensions:**
- Python (Microsoft)
- TypeScript and JavaScript Language Features
- React snippets
- Tailwind CSS IntelliSense
- GitLens

**Workspace Settings (`.vscode/settings.json`):**
```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "typescript.preferences.importModuleSpecifier": "relative",
  "tailwindCSS.includeLanguages": {
    "typescript": "javascript",
    "typescriptreact": "javascript"
  }
}
```

## Code Style and Standards

### Python Standards

#### Code Style

- **Formatter**: Follow PEP 8 with line length of 88 characters
- **Import Organization**: Use `isort` for import sorting
- **Type Hints**: Use type hints for all function signatures
- **Docstrings**: Use Google-style docstrings

**Example Function:**
```python
def recommend_recipes(
    self,
    desired_time: int,
    desired_complexity: int,
    desired_ingredients: int,
    n_recommendations: int = 20
) -> pd.DataFrame:
    """
    Recommend recipes based on user preferences.

    Args:
        desired_time: Preferred cooking time in minutes.
        desired_complexity: Preferred complexity score (0-100).
        desired_ingredients: Preferred number of ingredients.
        n_recommendations: Number of recommendations to return.

    Returns:
        DataFrame containing recommended recipes.

    Raises:
        ValueError: If input parameters are invalid.
    """
```

#### Error Handling

```python
# Good: Specific exception handling
try:
    recommender = joblib.load(model_path)
except FileNotFoundError:
    logger.error(f"Model file not found: {model_path}")
    return None
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    return None

# Bad: Broad exception catching without logging
try:
    recommender = joblib.load(model_path)
except:
    return None
```

#### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.info("[register] successful registration | email=%s", email)
logger.warning("[rate-limit] IP limit exceeded | ip=%s", ip)
logger.error("[auth] authentication failed | error=%s", str(e))
```

### TypeScript/React Standards

#### Code Style

- **Formatter**: Use Prettier with default settings
- **Naming**: Use camelCase for variables, PascalCase for components
- **Exports**: Prefer default exports for components
- **Props**: Define interfaces for all component props

**Example Component:**
```typescript
interface SaveButtonProps {
    recipeId: string;
    size?: 'sm' | 'md' | 'lg';
    onSaveChange?: (isSaved: boolean) => void;
}

export default function SaveButton({
    recipeId,
    size = 'sm',
    onSaveChange
}: SaveButtonProps) {
    // Component implementation
}
```

#### React Patterns

**Use Functional Components with Hooks:**
```typescript
// Good: Functional component with hooks
export default function RecipeList() {
    const [recipes, setRecipes] = useState<Recipe[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Effect implementation
    }, []);

    return <div>{/* Component JSX */}</div>;
}
```

**Error Boundaries:**
```typescript
// Implement error boundaries for robust error handling
export default function ErrorBoundary({ children }: { children: ReactNode }) {
    // Error boundary implementation
}
```

#### State Management

```typescript
// Use local state for component-specific data
const [formData, setFormData] = useState<FormData>({});

// Use context for global state
const { user, setUser } = useAuth();

// Use custom hooks for reusable logic
const { savedRecipes, toggleSave } = useSavedRecipes();
```

### Database Standards

#### Schema Design

- **Naming**: Use snake_case for table and column names
- **Constraints**: Always define appropriate constraints
- **Indexes**: Add indexes for frequently queried columns
- **Foreign Keys**: Use explicit foreign key relationships

**Example Migration:**
```python
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(100), nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

#### Query Optimization

```python
# Good: Use joins for related data
users_with_recipes = db.session.query(User).join(SavedRecipe).all()

# Good: Use pagination for large datasets
recipes = Recipe.query.paginate(
    page=page, per_page=20, error_out=False
)

# Bad: N+1 query problem
for user in users:
    user.saved_recipes  # Don't do this in loops
```

## Development Workflow

### Git Workflow

#### Branch Naming

- `feature/feature-name` - New features
- `bugfix/issue-description` - Bug fixes
- `hotfix/critical-issue` - Critical production fixes
- `docs/documentation-update` - Documentation changes
- `refactor/component-name` - Code refactoring

#### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Format: type(scope): description

feat(auth): add password reset functionality
fix(api): resolve recipe search pagination issue
docs(readme): update deployment instructions
refactor(frontend): extract reusable button component
test(auth): add integration tests for login flow
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/modifications
- `chore`: Maintenance tasks

#### Branch Management

```bash
# Create feature branch
git checkout -b feature/recipe-collections

# Keep feature branch updated
git fetch upstream
git rebase upstream/main

# Squash commits before PR
git rebase -i upstream/main
```

### Code Review Process

#### Before Submitting

1. **Self-Review Checklist:**
   - [ ] Code follows style guidelines
   - [ ] All tests pass
   - [ ] Documentation updated
   - [ ] No sensitive data committed
   - [ ] Performance implications considered

2. **Testing Requirements:**
   ```bash
   # Backend tests
   make test-cov  # Must maintain >90% coverage

   # Frontend tests
   make test-frontend-cov  # Must maintain >85% coverage

   # Integration tests
   make test-live  # Must pass against running backend
   ```

#### Review Guidelines

**For Reviewers:**
- Focus on code quality, security, and maintainability
- Provide constructive feedback with examples
- Test the changes locally when possible
- Check for accessibility and performance implications

**For Authors:**
- Respond to all review comments
- Make requested changes in separate commits
- Explain complex implementation decisions
- Update documentation as needed

### Release Process

#### Version Management

```bash
# Update version in pyproject.toml and package.json
# Follow semantic versioning (MAJOR.MINOR.PATCH)

# Tag release
git tag -a v1.2.0 -m "Release version 1.2.0"
git push upstream v1.2.0
```

#### Release Checklist

- [ ] All tests pass on main branch
- [ ] Documentation updated
- [ ] Migration scripts tested
- [ ] Security scan completed
- [ ] Performance benchmarks met
- [ ] Deployment tested in staging

## Testing Guidelines

### Backend Testing

#### Unit Tests

```python
# Test file: tests/test_auth.py
import pytest
from food_recipe_recommender.app import create_app
from food_recipe_recommender.app.models import User

@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app

def test_user_registration(client):
    """Test user registration endpoint."""
    response = client.post('/api/register', json={
        'email': 'test@example.com',
        'password': 'testpass123',
        'full_name': 'Test User'
    })
    assert response.status_code == 200
    assert response.json['success'] is True
```

#### Integration Tests

```python
# Test file: tests/test_integration_live.py
def test_recipe_search_integration():
    """Test live recipe search functionality."""
    filters = {'query': 'chicken'}
    response = search_recipes(filters)

    assert len(response['recipes']) > 0
    assert all('chicken' in recipe['name'].lower()
               for recipe in response['recipes'][:5])
```

### Frontend Testing

#### Component Tests

```typescript
// Test file: src/js/components/__tests__/SaveButton.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SaveButton from '../SaveButton';

describe('SaveButton', () => {
    it('toggles save state when clicked', async () => {
        render(<SaveButton recipeId="123" />);

        const button = screen.getByRole('button');
        fireEvent.click(button);

        await waitFor(() => {
            expect(button).toHaveTextContent('Saved');
        });
    });
});
```

#### Service Tests

```typescript
// Test file: src/js/services/__tests__/api.test.ts
import { searchRecipes } from '../api';

describe('API Service', () => {
    it('handles search with filters', async () => {
        const filters = { query: 'pasta', cookTime: 30 };
        const response = await searchRecipes(filters);

        expect(response.recipes).toBeDefined();
        expect(response.total).toBeGreaterThan(0);
    });
});
```

### ML Model Testing

#### Model Validation

```python
# Test file: tests/test_ml_model.py
def test_model_recommendations():
    """Test model recommendation quality."""
    recommender = RecipeRecommender(test_data)

    recommendations = recommender.recommend_recipes(
        desired_time=30,
        desired_complexity=25,
        desired_ingredients=10
    )

    assert len(recommendations) == 20
    assert all(rec['minutes'] <= 60 for rec in recommendations)
    assert recommendations.iloc[0]['similarity_distance'] <= \
           recommendations.iloc[-1]['similarity_distance']
```

### Performance Testing

```python
# Test file: tests/test_performance.py
import time

def test_recommendation_performance():
    """Test recommendation response time."""
    start_time = time.time()

    recommendations = recommender.recommend_recipes(30, 25, 10)

    end_time = time.time()
    assert end_time - start_time < 0.5  # Should complete in <500ms
```

## Documentation Standards

### Code Documentation

#### Python Docstrings

```python
def validate_numeric_range(
    value: float,
    min_val: float,
    max_val: float,
    param_name: str
) -> float:
    """
    Validate that a numeric value falls within a specified range.

    Args:
        value: The numeric value to validate.
        min_val: Minimum allowed value (inclusive).
        max_val: Maximum allowed value (inclusive).
        param_name: Name of the parameter for error messages.

    Returns:
        The validated value if within range.

    Raises:
        ValueError: If value is outside the allowed range.

    Example:
        >>> validate_numeric_range(25, 0, 100, "complexity")
        25
        >>> validate_numeric_range(-5, 0, 100, "complexity")
        ValueError: complexity must be between 0 and 100
    """
```

#### TypeScript Documentation

```typescript
/**
 * Hook for managing saved recipes with caching and optimistic updates.
 *
 * @returns Object containing saved recipes state and mutation functions
 *
 * @example
 * ```tsx
 * function RecipeCard({ recipe }) {
 *   const { isSaved, toggleSave, isLoading } = useSavedRecipes();
 *
 *   return (
 *     <button onClick={() => toggleSave(recipe.id)} disabled={isLoading}>
 *       {isSaved(recipe.id) ? 'Saved' : 'Save'}
 *     </button>
 *   );
 * }
 * ```
 */
export function useSavedRecipes() {
    // Implementation
}
```

### API Documentation

Update API documentation when adding/modifying endpoints:

```markdown
#### Create Saved Recipe Collection

```http
POST /api/collections
```

**Description:** Create a new recipe collection for the authenticated user.

**Authentication:** Required

**Request Body:**
```json
{
  "name": "My Favorite Pasta Dishes",
  "description": "Collection of pasta recipes I love",
  "recipe_ids": ["123", "456", "789"]
}
```
```

### README Updates

When adding new features, update relevant README sections:

- Installation instructions
- Configuration options
- Usage examples
- API endpoints
- Deployment notes

## Pull Request Process

### PR Creation Checklist

Before creating a pull request:

- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] Documentation updated for new features
- [ ] Self-reviewed the changes
- [ ] Added/updated tests for new functionality
- [ ] Considered security implications
- [ ] Checked for accessibility compliance (frontend)

### PR Template

```markdown
## Description
Brief description of changes and their purpose.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that causes existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
Include screenshots for UI changes.

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed the code
- [ ] Commented hard-to-understand areas
- [ ] Updated documentation
- [ ] Added tests for new functionality
- [ ] All tests pass
```

### Review Process

1. **Automated Checks**
   - CI/CD pipeline runs tests
   - Code coverage analysis
   - Security scanning
   - Dependency checking

2. **Human Review**
   - At least one reviewer approval required
   - Focus on code quality, security, performance
   - Documentation completeness

3. **Merge Requirements**
   - All automated checks pass
   - All review comments resolved
   - Up-to-date with main branch
   - No merge conflicts

## Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
**Bug Description**
Clear description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g. iOS, Windows, Ubuntu]
- Browser: [e.g. chrome, safari]
- Version: [e.g. 22]

**Additional Context**
Any other context about the problem.
```

### Feature Requests

Use the feature request template:

```markdown
**Feature Summary**
Brief summary of the feature.

**Problem Statement**
What problem does this feature solve?

**Proposed Solution**
Detailed description of the proposed feature.

**Alternatives Considered**
Other solutions you've considered.

**Additional Context**
Any other context or screenshots.
```

### Security Issues

For security vulnerabilities:

1. **Do NOT** create a public issue
2. Email security@project-domain.com
3. Include detailed description and steps to reproduce
4. Allow time for investigation before public disclosure

## Security Guidelines

### Secure Coding Practices

#### Input Validation

```python
# Always validate and sanitize inputs
@auth_bp.post('/api/register')
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email', '').strip()
    if not email or '@' not in email:
        return jsonify({'error': 'Valid email required'}), 400
```

#### SQL Injection Prevention

```python
# Good: Use parameterized queries
user = User.query.filter_by(email=email).first()

# Bad: String concatenation
query = f"SELECT * FROM users WHERE email = '{email}'"  # Never do this
```

#### XSS Prevention

```typescript
// Good: React automatically escapes content
return <div>{userInput}</div>;

// Bad: Dangerous HTML injection
return <div dangerouslySetInnerHTML={{__html: userInput}} />;
```

#### Authentication Security

```python
# Use secure password hashing
password_hash = generate_password_hash(password)

# Validate session tokens
if not current_user.is_authenticated:
    return jsonify({'error': 'Authentication required'}), 401

# Rate limiting for sensitive endpoints
if request_count > RATE_LIMIT:
    return jsonify({'error': 'Rate limit exceeded'}), 429
```

### Environment Security

```env
# Good: Use strong secrets
SECRET_KEY=randomly-generated-32-byte-key

# Bad: Weak or default secrets
SECRET_KEY=dev  # Never in production

# Keep sensitive data in environment variables
RESEND_API_KEY=re_your_api_key_here
DATABASE_URL=postgresql://user:pass@host/db

# Never commit .env files to version control
```

## Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment:

- **Be respectful** in all interactions
- **Be constructive** in feedback and criticism
- **Be inclusive** and welcoming to contributors of all backgrounds
- **Focus on the code**, not personal attributes
- **Help others learn** and grow

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **Pull Requests**: Code review and discussion
- **Discussions**: General questions and community chat

### Getting Help

1. **Check Documentation**: Review existing docs first
2. **Search Issues**: Look for similar problems/solutions
3. **Ask Questions**: Create a discussion or issue
4. **Provide Context**: Include relevant details and examples

### Recognition

We appreciate all contributions:

- Contributors are listed in project documentation
- Significant contributions are highlighted in release notes
- Community members can become maintainers over time

### Mentorship

New contributors are welcome:

- Look for "good first issue" labels
- Ask for guidance on complex issues
- Pair programming sessions available for learning
- Code review as learning opportunity

---

Thank you for contributing to Recipe Recommender! Your contributions help make this project better for everyone. 🎉

For questions about contributing, please create a GitHub Discussion or reach out to the maintainers.
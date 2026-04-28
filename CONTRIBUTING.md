# Contributing to SQL to NoSQL Converter

First off, thank you for considering contributing to SQL to NoSQL Converter! 🎉

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

### Our Standards

- ✅ Be respectful and inclusive
- ✅ Welcome newcomers and help them learn
- ✅ Focus on what is best for the community
- ✅ Show empathy towards other community members
- ❌ No harassment, trolling, or discriminatory language
- ❌ No personal or political attacks

## Getting Started

### Prerequisites

- Python 3.13+ with Anaconda
- Node.js 18+
- Git
- BlazeAPI key or Ollama installed

### Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/sql-nosql-converter.git
cd sql-nosql-converter

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/sql-nosql-converter.git
```

## Development Setup

### Backend Setup

```bash
cd backend

# Create conda environment
conda create -n fastapi_env python=3.13
conda activate fastapi_env

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your credentials

# Run backend
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env
# Edit .env if needed

# Run frontend
npm run dev
```

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Screenshots** (if applicable)
- **Environment details** (OS, Python version, Node version)

**Bug Report Template:**

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g., Windows 11]
- Python: [e.g., 3.13]
- Node: [e.g., 18.17]
- Browser: [e.g., Chrome 120]
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description**
- **Use case** - Why is this enhancement useful?
- **Proposed solution**
- **Alternative solutions** you've considered
- **Mockups or examples** (if applicable)

### Your First Code Contribution

Unsure where to begin? Look for issues labeled:

- `good first issue` - Simple issues for beginners
- `help wanted` - Issues that need assistance
- `documentation` - Documentation improvements

## Coding Standards

### Python (Backend)

```python
# Follow PEP 8 style guide
# Use type hints
def convert_schema(sql: str, target_db: str) -> Dict[str, Any]:
    """Convert SQL schema to target database.
    
    Args:
        sql: SQL DDL statements
        target_db: Target database (mongodb, cassandra, neo4j)
        
    Returns:
        Conversion result with schema and metadata
    """
    pass

# Use docstrings for all functions
# Keep functions small and focused
# Use meaningful variable names
```

**Tools:**
- `black` for code formatting
- `flake8` for linting
- `mypy` for type checking

```bash
# Format code
black backend/

# Lint code
flake8 backend/

# Type check
mypy backend/
```

### TypeScript (Frontend)

```typescript
// Use TypeScript strict mode
// Define interfaces for all data structures
interface ConversionResult {
  schema: string;
  explanation: string;
  warnings: string[];
  stats: DatabaseStats;
  score: number;
}

// Use functional components with hooks
const MyComponent: React.FC<Props> = ({ data }) => {
  const [state, setState] = useState<string>('');
  
  return <div>{data}</div>;
};

// Use meaningful names
// Keep components small and focused
```

**Tools:**
- `prettier` for code formatting
- `eslint` for linting

```bash
# Format code
npm run format

# Lint code
npm run lint
```

### File Structure

```
backend/
├── ai/              # AI enhancement logic
├── converters/      # Database converters
├── database/        # Database connections
├── parsers/         # SQL parsers
├── models.py        # Pydantic models
├── config.py        # Configuration
└── main.py          # FastAPI app

frontend/
├── src/
│   ├── components/  # React components
│   ├── services/    # API services
│   ├── App.tsx      # Main app
│   └── main.tsx     # Entry point
└── public/          # Static assets
```

## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```bash
# Feature
git commit -m "feat(mongodb): add realistic sample document generation"

# Bug fix
git commit -m "fix(parser): handle complex JOIN statements correctly"

# Documentation
git commit -m "docs(readme): update installation instructions"

# Refactor
git commit -m "refactor(converter): simplify embedding strategy logic"
```

### Commit Message Rules

- ✅ Use present tense ("add feature" not "added feature")
- ✅ Use imperative mood ("move cursor to..." not "moves cursor to...")
- ✅ Limit first line to 72 characters
- ✅ Reference issues and PRs in footer

## Pull Request Process

### Before Submitting

1. **Update your fork**
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Write clean, documented code
   - Add tests for new features
   - Update documentation

4. **Test your changes**
   ```bash
   # Backend tests
   cd backend
   python -m pytest
   
   # Frontend tests
   cd frontend
   npm run lint
   npm run build
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Backend tests pass
- [ ] Frontend tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added/updated
- [ ] All tests passing

## Screenshots (if applicable)
Add screenshots here

## Related Issues
Closes #123
```

### Review Process

1. **Automated checks** must pass (linting, tests)
2. **Code review** by at least one maintainer
3. **Changes requested** - Address feedback and push updates
4. **Approval** - PR will be merged by maintainer

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_converters.py

# Run with coverage
python -m pytest --cov=. --cov-report=html
```

### Frontend Tests

```bash
cd frontend

# Type checking
npm run lint

# Build test
npm run build

# Manual testing
npm run dev
```

### Integration Tests

```bash
# Test complete flow
cd scripts
python test_api.py
python test_parallel_execution.py
python test_blazeapi.py
```

## Documentation

### Code Documentation

- **Python**: Use docstrings (Google style)
- **TypeScript**: Use JSDoc comments
- **README**: Update for new features
- **API Docs**: Update OpenAPI schema

### Documentation Structure

```
docs/
├── setup/           # Setup guides
├── guides/          # Technical guides
├── troubleshooting/ # Common issues
└── reports/         # Project reports
```

### Writing Documentation

- ✅ Clear and concise
- ✅ Include code examples
- ✅ Add screenshots/diagrams
- ✅ Keep up-to-date
- ✅ Test all commands

## Areas for Contribution

### High Priority

- 🔧 Add PostgreSQL converter
- 🔧 Implement query translation (SQL → MQL/CQL/Cypher)
- 🧪 Increase test coverage
- 📝 Improve AI prompts
- 🌍 Add internationalization (i18n)

### Medium Priority

- 🎨 UI/UX improvements
- 📊 Add more visualization options
- 🔌 Add DynamoDB converter
- 📚 Expand documentation
- ⚡ Performance optimizations

### Low Priority

- 🎨 Theme customization
- 📱 Mobile responsiveness
- 🔔 Notification system
- 📤 Export to file functionality
- 🔍 Advanced search in history

## Questions?

- 📖 Check [Documentation](docs/)
- 💬 Ask in [Discussions](https://github.com/yourusername/sql-nosql-converter/discussions)
- 🐛 Report [Issues](https://github.com/yourusername/sql-nosql-converter/issues)

## Recognition

Contributors will be recognized in:

- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing! 🚀

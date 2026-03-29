# Contributing to CareerOS

Thank you for your interest in contributing to CareerOS! This document provides guidelines and instructions for contributing.

## 🌟 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear descriptive title**
- **Detailed steps to reproduce**
- **Expected vs actual behavior**
- **Screenshots** (if applicable)
- **Environment details** (OS, browser, Python/Node versions)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear descriptive title**
- **Step-by-step description** of the suggested enhancement
- **Explain why** this enhancement would be useful
- **List alternatives** you've considered

### Pull Requests

1. **Fork & Clone**
   ```bash
   git clone https://github.com/yourusername/ApplyWise.git
   cd ApplyWise
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/amazing-feature
   # or
   git checkout -b fix/bug-description
   ```

3. **Make Your Changes**
   - Follow existing code style
   - Write meaningful commit messages
   - Add tests if applicable
   - Update documentation

4. **Test Your Changes**
   ```bash
   # Backend tests
   cd apps/api
   pytest

   # Frontend tests
   cd apps/web
   npm test
   ```

5. **Commit & Push**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   git push origin feature/amazing-feature
   ```

6. **Open a Pull Request**
   - Use a clear, descriptive title
   - Reference any related issues
   - Describe your changes in detail
   - Include screenshots for UI changes

## 📝 Code Style Guidelines

### Python (Backend)

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints where possible
- Document functions with docstrings
- Keep functions small and focused
- Use meaningful variable names

```python
# Good
def calculate_match_score(user_skills: list[str], job_requirements: list[str]) -> float:
    """Calculate matching score between user skills and job requirements.

    Args:
        user_skills: List of user's skill strings
        job_requirements: List of required skill strings

    Returns:
        Float between 0.0 and 1.0 representing match percentage
    """
    # Implementation
    pass

# Bad
def calc(u, j):
    pass
```

### TypeScript/React (Frontend)

- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks
- Keep components small and reusable
- Use meaningful component and prop names

```typescript
// Good
interface JobCardProps {
  job: Job;
  onApply: (jobId: string) => void;
  matchScore?: number;
}

export function JobCard({ job, onApply, matchScore }: JobCardProps) {
  // Implementation
}

// Bad
function Card(props: any) {
  // Implementation
}
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation changes
- `style:` formatting, missing semicolons, etc.
- `refactor:` code restructuring
- `test:` adding tests
- `chore:` maintenance tasks

Examples:
```
feat: add resume generation API endpoint
fix: resolve token expiration bug in auth middleware
docs: update installation instructions in README
refactor: extract matching logic into separate service
```

## 🧪 Testing

### Backend Testing

```bash
cd apps/api
pytest tests/
pytest tests/test_matching.py -v  # Specific test file
pytest -k "test_auth" -v          # Tests matching pattern
```

### Frontend Testing

```bash
cd apps/web
npm test              # Run all tests
npm test -- --watch   # Watch mode
npm run test:coverage # Coverage report
```

## 🔍 Code Review Process

1. All PRs require at least one review
2. Address review comments promptly
3. Keep PRs focused and reasonably sized
4. Ensure CI/CD checks pass
5. Update CHANGELOG.md for significant changes

## 🐛 Debugging Tips

### Backend Debugging

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
uvicorn app.main:app --reload

# Use pdb for debugging
import pdb; pdb.set_trace()
```

### Frontend Debugging

- Use React DevTools
- Check browser console for errors
- Use Network tab for API debugging
- Use `console.log()` or debugger statements

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [PostgreSQL with pgvector](https://github.com/pgvector/pgvector)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

## 🤝 Community

- Be respectful and inclusive
- Help others learn and grow
- Share knowledge and experiences
- Celebrate successes together

## ❓ Questions?

Feel free to open a [GitHub Discussion](https://github.com/yourusername/ApplyWise/discussions) if you have questions!

---

**Thank you for contributing to CareerOS! 🚀**

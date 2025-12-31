# Contributing to SecurePay AI

> **Project Author**: Md. Tanvir Hossain  
> **Contact**: tanvir.eece.cse@gmail.com  
> **GitHub**: [@tanvir-eece-cse](https://github.com/tanvir-eece-cse)

First off, thank you for considering contributing to SecurePay AI! It's people like you that make this project such a great tool for Bangladesh's FinTech ecosystem.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps to reproduce the problem**
* **Provide specific examples**
* **Describe the behavior you observed and what you expected**
* **Include logs and error messages**
* **Specify your environment** (OS, Python version, Node version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior and expected behavior**
* **Explain why this enhancement would be useful**

### Pull Requests

* Fill in the required template
* Follow the coding style guides
* Include appropriate test cases
* Update documentation as needed
* End all files with a newline
* Ensure CI/CD pipeline passes

## Development Setup

### Prerequisites

* Python 3.11+
* Node.js 18+
* Docker & Docker Compose
* PostgreSQL 15+
* Redis 7+

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/securepay-ai-fraud-detection.git
   cd securepay-ai-fraud-detection
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your configuration
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

3. **ML Service Setup**
   ```bash
   cd ml-service
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8001
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Using Docker Compose**
   ```bash
   docker-compose up -d
   ```

## Coding Style

### Python (Backend & ML Service)

* Follow [PEP 8](https://pep8.org/)
* Use type hints
* Maximum line length: 100 characters
* Use `black` for code formatting
* Use `isort` for import sorting
* Use `flake8` for linting
* Use `mypy` for type checking

```bash
black app/
isort app/
flake8 app/
mypy app/
```

### TypeScript/React (Frontend)

* Follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
* Use ESLint with the provided configuration
* Use Prettier for formatting
* Use functional components with hooks
* Use TypeScript strict mode

```bash
npm run lint
npm run format
```

### Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

Example:
```
feat: Add real-time fraud detection alerts

- Implement WebSocket connection for live alerts
- Add notification system using react-hot-toast
- Update backend to emit events via Kafka
- Add comprehensive tests

Closes #123
```

### Commit Types

* `feat`: A new feature
* `fix`: A bug fix
* `docs`: Documentation only changes
* `style`: Changes that don't affect code meaning
* `refactor`: Code change that neither fixes a bug nor adds a feature
* `perf`: Code change that improves performance
* `test`: Adding missing tests
* `chore`: Changes to build process or auxiliary tools

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ --cov=app --cov-report=html
```

### ML Service Tests

```bash
cd ml-service
pytest tests/ --cov=app
```

### Frontend Tests

```bash
cd frontend
npm run test
npm run test:coverage
```

### Integration Tests

```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## Security

### Reporting Security Issues

**Do not open public issues for security vulnerabilities.**

Email security concerns to: security@securepay.com.bd

Include:
* Description of the vulnerability
* Steps to reproduce
* Potential impact
* Suggested fix (if any)

### Security Checklist

* [ ] No hardcoded secrets or credentials
* [ ] Sensitive data is encrypted
* [ ] Authentication and authorization are properly implemented
* [ ] Input validation is comprehensive
* [ ] SQL injection is prevented
* [ ] XSS vulnerabilities are addressed
* [ ] CSRF protection is in place
* [ ] Dependencies are up to date
* [ ] Security headers are configured

## Documentation

* Update README.md if you change functionality
* Add docstrings to all functions and classes
* Update API documentation for endpoint changes
* Include examples for new features
* Keep the architecture diagram up to date

## Review Process

1. Create a feature branch from `develop`
2. Make your changes
3. Write or update tests
4. Ensure all tests pass
5. Update documentation
6. Create a pull request to `develop`
7. Address review comments
8. Once approved, it will be merged

## Release Process

1. Merge `develop` into `main`
2. Tag the release
3. CI/CD automatically deploys to production
4. Create release notes
5. Announce on relevant channels

## Recognition

Contributors will be recognized in:
* README.md Contributors section
* Release notes
* Project documentation

## Questions?

Feel free to open an issue with the `question` label or reach out to the maintainers.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to SecurePay AI! 🚀

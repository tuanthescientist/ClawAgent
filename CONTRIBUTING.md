# ClawAgent Contributing Guide

## Getting Started

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/ClawAgent.git
cd ClawAgent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
make install

# Run tests
make test
```

## Code Style

We use:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking

Run before committing:
```bash
make format
make lint
```

## Testing

All new features must include tests:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src

# Run specific test file
pytest tests/test_main.py -v
```

## Pull Request Process

1. Update documentation as needed
2. Add tests for new functionality
3. Run `make lint` and `make format`
4. Run `make test` to ensure all tests pass
5. Update README.md if needed
6. Submit PR with clear description

## Reporting Issues

Use GitHub Issues with:
- Clear title
- Detailed description
- Steps to reproduce
- Expected vs actual behavior
- Environment info (Python version, OS, etc.)

## License

By contributing, you agree that your contributions will be licensed under its MIT License.

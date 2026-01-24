# Contributing to GateKeeper

Thank you for considering contributing to GateKeeper! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
   ```bash
   git clone https://github.com/YOUR_USERNAME/GateKeeper.git
   cd GateKeeper
   ```
3. **Create a branch** for your changes
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

Follow the development setup instructions in the [README.md](README.md#development).

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions small and focused
- Write self-documenting code

## Making Changes

1. **Make your changes** in your feature branch
2. **Test your changes** thoroughly
3. **Commit your changes** with clear, descriptive commit messages
   ```bash
   git commit -m "Add feature: description of what you added"
   ```
4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Submit a Pull Request** to the main repository

## Pull Request Guidelines

- **Title**: Clear and descriptive
- **Description**: Explain what your PR does and why
- **Changes**: List the main changes made
- **Testing**: Describe how you tested your changes
- **Screenshots**: Include screenshots for UI changes
- **Documentation**: Update documentation if needed

## Commit Message Guidelines

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

Example:
```
Add bulk email retry functionality

- Implement retry logic for failed email deliveries
- Add retry_count and next_retry_at fields to EmailLog
- Create retry_failed_emails endpoint
- Update email service to handle retries

Fixes #123
```

## Code Review Process

1. A maintainer will review your PR
2. Address any feedback or requested changes
3. Once approved, your PR will be merged

## Reporting Bugs

Use the GitHub issue tracker to report bugs. Include:

- **Description**: Clear description of the bug
- **Steps to Reproduce**: Step-by-step instructions
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, Python version, etc.
- **Screenshots**: If applicable

## Suggesting Features

Use the GitHub issue tracker to suggest features. Include:

- **Description**: Clear description of the feature
- **Use Case**: Why is this feature needed?
- **Proposed Solution**: How should it work?
- **Alternatives**: Any alternative solutions considered

## Project Structure

```
GateKeeper/
├── app/
│   ├── models/          # Database models
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   ├── utils/           # Utilities
│   ├── templates/       # HTML templates
│   └── static/          # Static assets
├── migrations/          # Database migrations
├── examples/            # Example files
├── docker-compose.yml   # Docker services
└── requirements.txt     # Python dependencies
```

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for good test coverage

## Documentation

- Update README.md if needed
- Update API documentation
- Add docstrings to new functions
- Update plan.md for architectural changes

## Questions?

If you have questions, feel free to:
- Open an issue
- Ask in discussions
- Contact the maintainers

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

Thank you for contributing to GateKeeper! 🎉

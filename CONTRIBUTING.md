# Contributing to OSINT Social Media Monitoring App

Thank you for your interest in contributing to this project! This document provides guidelines for contributing.

## Code of Conduct

- Be respectful and professional
- Follow ethical OSINT practices
- Ensure all contributions respect privacy and legal boundaries
- Never contribute code that could be used for harassment or illegal activities

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. Create a new issue with:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (Python version, OS, etc.)

### Suggesting Enhancements

1. Open an issue describing:
   - The enhancement you'd like to see
   - Why it would be useful
   - How it aligns with ethical OSINT practices

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes:
   - Follow PEP 8 style guide
   - Add docstrings to functions
   - Include error handling
   - Update documentation if needed
4. Test your changes thoroughly
5. Submit a pull request with:
   - Clear description of changes
   - Reference to related issues
   - Any breaking changes noted

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/osint-app.git
cd osint-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Make your changes
# ...

# Test your changes
python osint_monitor.py "test keyword"
```

## Guidelines

### Code Quality

- Write clean, readable code
- Follow Python best practices
- Add comments for complex logic
- Handle errors gracefully

### Security

- Never commit API keys or credentials
- Use environment variables for sensitive data
- Validate and sanitize user inputs
- Follow secure coding practices

### Ethical Considerations

All contributions must:
- Respect rate limits and server resources
- Honor robots.txt and website ToS
- Not enable harassment or illegal activities
- Comply with data protection laws
- Include appropriate warnings and documentation

### Testing

- Test your code with various inputs
- Verify error handling works correctly
- Ensure rate limiting functions properly
- Test with and without API credentials

## Questions?

Feel free to open an issue for:
- Questions about contributing
- Clarification on guidelines
- Help with development setup

Thank you for contributing responsibly!

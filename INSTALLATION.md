# OSINT Monitor - Installation & Distribution Guide

Complete guide to installing and distributing the OSINT Monitor application.

## Installation Methods

### Method 1: Install from PyPI (Recommended - Coming Soon)

Once published to PyPI, installation will be as simple as:

```bash
pip install osint-monitor
```

Then use:

```bash
osint-monitor "keyword"
setup-twitter-api
```

### Method 2: Install from GitHub (Current)

```bash
# Clone the repository
git clone https://github.com/nrk8286/osint-app.git
cd osint-app

# Install in development mode
pip install -e .

# Or install normally
pip install .
```

### Method 3: Install from Local Source

```bash
# Navigate to project directory
cd /path/to/osint-app

# Install
pip install .

# Or with extras
pip install .[dev]
```

### Method 4: Development Installation

For developers who want to modify the code:

```bash
git clone https://github.com/nrk8286/osint-app.git
cd osint-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev tools
pip install -e .[dev]

# Run tests
pytest
```

## Package Structure

```
osint-app/
├── osint_monitor.py           # Main application
├── recon_ng_wrapper.py        # Recon-ng integration
├── recon_ng_examples.py       # Example scripts
├── setup_twitter_api.py       # Twitter API setup
├── example_usage.py           # Usage examples
├── setup.py                   # Setup configuration (legacy)
├── pyproject.toml             # Setup configuration (modern)
├── MANIFEST.in                # Package manifest
├── requirements.txt           # Pip dependencies
├── README.md                  # Project overview
├── LICENSE                    # MIT License
├── .env.example               # Configuration template
└── Documentation files...     # Various guides
```

## Building the Package

### Prerequisites

```bash
pip install build twine setuptools wheel
```

### Build Distribution

```bash
# Build wheel and source distribution
python -m build

# Output:
# dist/osint-monitor-1.0.0-py3-none-any.whl
# dist/osint-monitor-1.0.0.tar.gz
```

### Check Distribution

```bash
# Validate package metadata
twine check dist/*
```

### Upload to PyPI (Requires Account)

#### TestPyPI (Recommended for testing)

```bash
# Configure ~/.pypirc first with TestPyPI credentials

twine upload --repository testpypi dist/*

# Then test installation:
pip install --index-url https://test.pypi.org/simple/ osint-monitor
```

#### Production PyPI

```bash
# Only after successful TestPyPI testing

twine upload dist/*
```

## Console Scripts

After installation, two CLI commands are available:

### osint-monitor

Main application for OSINT investigation:

```bash
osint-monitor "keyword"
osint-monitor "nrk8286"
osint-monitor "example.com"
```

Options:
- `-h, --help` - Show help message
- `-v, --verbose` - Verbose output
- Interactive mode if no keyword provided

### setup-twitter-api

Configure Twitter API credentials:

```bash
setup-twitter-api                    # Interactive menu
setup-twitter-api --validate         # Check credentials
setup-twitter-api --test             # Test connection
setup-twitter-api --create-env       # Create .env file
```

## Dependencies

### Core Requirements

```
googlesearch-python>=1.2.3
tweepy>=4.14.0
requests>=2.31.0
beautifulsoup4>=4.12.0
pandas>=2.0.0
python-dotenv>=1.0.0
```

### Optional Dependencies

#### Development

```bash
pip install osint-monitor[dev]
```

Includes:
- pytest - Testing framework
- pytest-cov - Coverage reporting
- black - Code formatting
- flake8 - Linting
- mypy - Type checking

#### Recon-ng (Separate Installation)

```bash
git clone https://github.com/lanmaster53/recon-ng.git
cd recon-ng
pip install -r requirements.txt
sudo ln -s $(pwd)/recon-ng /usr/local/bin/recon-ng
```

See [RECON_NG_SETUP.md](RECON_NG_SETUP.md) for details.

## Post-Installation Setup

### 1. Create Environment File

```bash
# Create .env from template
cp /path/to/site-packages/osint_monitor/.env.example ~/.config/osint-monitor/.env

# Or copy from installed package location
python -c "import osint_monitor; print(osint_monitor.__file__)"
```

### 2. Configure Twitter API (Optional)

```bash
setup-twitter-api
```

### 3. Verify Installation

```bash
# Check version
python -c "import osint_monitor; print(osint_monitor.__version__)"

# Test import
python -c "from osint_monitor import OSINTMonitor; print('✅ OSINT Monitor installed successfully')"

# Test CLI
osint-monitor --help
```

## Troubleshooting Installation

### Issue: "command not found: osint-monitor"

Solution: Ensure pip installed the package correctly:

```bash
pip list | grep osint-monitor
```

If missing, reinstall:

```bash
pip install --force-reinstall osint-monitor
```

Add to PATH if necessary:

```bash
export PATH="$PATH:$(python -m site --user-scripts)"
```

### Issue: "ModuleNotFoundError"

Solution: Check dependencies are installed:

```bash
pip install -r requirements.txt
```

### Issue: "Permission denied" when installing

Solution: Use user installation:

```bash
pip install --user osint-monitor
```

Or use virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate
pip install osint-monitor
```

## Uninstallation

```bash
pip uninstall osint-monitor
```

## Version Management

Current version: **1.0.0**

Version format: `MAJOR.MINOR.PATCH`

- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes

## Publishing to PyPI

### Step 1: Prepare

```bash
# Update version in setup.py and pyproject.toml
# Update CHANGELOG
# Test locally
python -m build
twine check dist/*
```

### Step 2: Tag Release

```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### Step 3: Upload

```bash
# Test PyPI
twine upload --repository testpypi dist/osint-monitor-1.0.0*

# Production PyPI
twine upload dist/osint-monitor-1.0.0*
```

### Step 4: Verify

```bash
pip install osint-monitor==1.0.0
```

## Distribution Files

After building, you'll have:

- **osint-monitor-1.0.0.tar.gz** - Source distribution
  - Contains full source code
  - Cross-platform
  - Requires compilation of C extensions (if any)

- **osint-monitor-1.0.0-py3-none-any.whl** - Wheel distribution
  - Pre-built binary
  - Faster installation
  - Platform independent

## Platform Support

✅ **Supported:**
- Windows (7+)
- macOS (10.9+)
- Linux (all distributions)
- Python 3.7 - 3.12

## Development Distribution

### Create Local Package

```bash
# Build
python -m build

# Install locally from wheel
pip install dist/osint-monitor-1.0.0-py3-none-any.whl

# Or from source
pip install dist/osint-monitor-1.0.0.tar.gz
```

### Share with Others

```bash
# Generate wheel
python -m build --wheel

# Share the .whl file
# Others can install with:
pip install osint-monitor-1.0.0-py3-none-any.whl
```

## Docker Distribution (Optional)

For containerized deployment:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install -e .

ENTRYPOINT ["osint-monitor"]
CMD ["--help"]
```

Build and run:

```bash
docker build -t osint-monitor .
docker run osint-monitor "keyword"
```

## Continuous Integration

Automated testing and distribution:

```yaml
# GitHub Actions example
name: Test and Release

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install .[dev]
      - name: Run tests
        run: pytest
      - name: Build distribution
        run: python -m build
```

## Support

- **Issues**: https://github.com/nrk8286/osint-app/issues
- **Discussions**: https://github.com/nrk8286/osint-app/discussions
- **Documentation**: See README.md and guides in repository

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [setuptools Documentation](https://setuptools.pypa.io/)
- [Build Documentation](https://build.pypa.io/)
- [Twine Documentation](https://twine.readthedocs.io/)

---

**Ready to distribute!** 🚀

All packaging files are in place. The application is ready for:
- Local installation
- Distribution to others
- Publishing to PyPI
- Containerization

# OSINT Monitoring Platform v2.0

A production-ready, state-of-the-art OSINT (Open Source Intelligence) monitoring platform for tracking keyword mentions across multiple platforms with advanced features including sentiment analysis, async processing, REST API, and comprehensive data storage.

## 🚀 New Features in v2.0

### Core Enhancements
- ✨ **Modular Architecture**: Clean, maintainable package structure
- ⚡ **Async/Await Support**: Concurrent API calls for 3-5x faster data collection
- 🎯 **Type Hints**: Full type safety with Pydantic models
- 🗄️ **Database Storage**: SQLite/PostgreSQL support with SQLAlchemy
- 📊 **Advanced Analytics**: Sentiment analysis using Hugging Face transformers

### New Data Sources
- 🔍 **Google Search**: Enhanced integration
- 🐦 **Twitter/X**: Full API v2 support
- 🤖 **Reddit**: Complete PRAW integration
- 📰 **News API**: Real-time news monitoring

### Developer Experience
- 🎨 **Rich CLI**: Beautiful terminal interface with progress bars and tables
- 🔌 **REST API**: FastAPI-powered API with OpenAPI documentation
- 🐳 **Docker Support**: Production-ready containerization
- 🧪 **Comprehensive Tests**: pytest suite with 80%+ coverage
- 📝 **Full Type Safety**: MyPy validated

### Production Features
- 🔒 **Security**: Environment-based secrets management
- 📈 **Monitoring**: Built-in metrics and logging
- 🚦 **CI/CD**: GitHub Actions workflow
- 💾 **Caching**: Optional Redis support
- 🎛️ **Configuration**: Pydantic settings with validation

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [CLI Usage](#cli-usage)
  - [API Usage](#api-usage)
  - [Programmatic Usage](#programmatic-usage)
- [Configuration](#configuration)
- [Docker Deployment](#docker-deployment)
- [Development](#development)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Contributing](#contributing)

## 🛠️ Installation

### Prerequisites
- Python 3.10 or higher
- pip or poetry
- Git

### Option 1: Standard Installation

```bash
# Clone the repository
git clone https://github.com/nrk8286/osint-app.git
cd osint-app

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Option 2: Docker Installation

```bash
# Clone and build
git clone https://github.com/nrk8286/osint-app.git
cd osint-app

# Start with docker-compose
docker-compose up -d
```

## ⚡ Quick Start

### 1. Configure API Keys

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API credentials
nano .env  # or use your preferred editor
```

### 2. Run Your First Search

```bash
# Using the CLI
osint-monitor "artificial intelligence" --output results.json

# Or using Python
python -m osint_app.cli "cybersecurity" --google 20 --twitter 20
```

### 3. Start the API Server

```bash
# Start FastAPI server
uvicorn osint_app.api.main:app --reload

# Visit http://localhost:8000/docs for interactive API documentation
```

## 💻 Usage

### CLI Usage

The enhanced CLI provides a beautiful terminal interface with rich formatting:

```bash
# Basic search
osint-monitor "keyword"

# Advanced search with options
osint-monitor "data breach" \
    --google 20 \
    --twitter 30 \
    --reddit 15 \
    --news 10 \
    --output breach_report.json

# View statistics
osint-monitor --stats --days 30

# Save to CSV
osint-monitor "machine learning" --output ml_mentions.csv
```

**CLI Options:**
- `--google N`: Number of Google results (default: 10)
- `--twitter N`: Number of Twitter results (default: 10)
- `--reddit N`: Number of Reddit results (default: 10)
- `--news N`: Number of News results (default: 10)
- `--output FILE`: Save to file (.csv or .json)
- `--stats`: Show database statistics
- `--days N`: Days for statistics (default: 7)

### API Usage

Start the API server:

```bash
# Development mode
uvicorn osint_app.api.main:app --reload --port 8000

# Production mode
uvicorn osint_app.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**API Endpoints:**

```bash
# Search for mentions
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "cybersecurity", "google_results": 10}'

# Get stored mentions
curl "http://localhost:8000/api/mentions?keyword=cybersecurity&limit=50"

# Get statistics
curl "http://localhost:8000/api/stats?days=7"

# Analyze sentiment
curl -X POST "http://localhost:8000/api/analyze/sentiment?text=This is amazing!"

# Health check
curl "http://localhost:8000/health"
```

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation.

### Programmatic Usage

```python
import asyncio
from osint_app.core.monitor import OSINTMonitor

# Create monitor instance
monitor = OSINTMonitor(
    use_database=True,
    enable_sentiment=True
)

# Async search
async def main():
    mentions = await monitor.collect_mentions(
        keyword="artificial intelligence",
        google_results=20,
        twitter_results=20,
        reddit_results=15,
        news_results=10
    )

    # Save results
    monitor.save_to_json("ai_mentions.json")

    # Get statistics
    stats = monitor.get_stats(days=7)
    print(stats)

# Run
asyncio.run(main())

# Or use synchronous wrapper
from osint_app.core.monitor import collect_mentions_sync

mentions = collect_mentions_sync(
    keyword="python programming",
    google_results=10
)
```

## ⚙️ Configuration

Configuration is managed through environment variables and Pydantic settings.

### Environment Variables

Create a `.env` file (see `.env.example`):

```bash
# Twitter API
TWITTER_BEARER_TOKEN=your_token_here

# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=OSINT-Monitor/2.0

# News API
NEWS_API_KEY=your_api_key

# Database
DB_URL=sqlite:///osint_data.db  # or postgresql://user:pass@host/db

# Redis (optional)
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379

# Features
ENABLE_SENTIMENT_ANALYSIS=true
ENABLE_CACHING=false

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
```

### API Credentials Setup

#### Twitter API
1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a project and app
3. Generate Bearer Token
4. Add to `.env`

#### Reddit API
1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Create an app (script type)
3. Copy client ID and secret
4. Add to `.env`

#### News API
1. Sign up at [NewsAPI.org](https://newsapi.org/)
2. Get your API key
3. Add to `.env`

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services:
- **osint-app**: Main application on port 8000
- **redis**: Cache server on port 6379
- **postgres**: Optional database on port 5432

### Using Docker Directly

```bash
# Build image
docker build -t osint-monitoring .

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/.env:/app/.env \
  --name osint-app \
  osint-monitoring

# View logs
docker logs -f osint-app
```

## 👨‍💻 Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run tests
pytest

# Run with coverage
pytest --cov=osint_app --cov-report=html

# Format code
black osint_app/
isort osint_app/

# Type check
mypy osint_app/

# Lint
flake8 osint_app/
```

### Project Structure

```
osint-app/
├── osint_app/              # Main package
│   ├── core/               # Core functionality
│   │   ├── config.py       # Configuration management
│   │   └── monitor.py      # Main monitor class
│   ├── sources/            # Data source integrations
│   │   ├── base.py         # Base source class
│   │   ├── google.py       # Google search
│   │   ├── twitter.py      # Twitter API
│   │   ├── reddit.py       # Reddit API
│   │   └── news.py         # News API
│   ├── storage/            # Storage backends
│   │   ├── database.py     # Database storage
│   │   └── models.py       # SQLAlchemy models
│   ├── api/                # FastAPI application
│   │   └── main.py         # API routes
│   ├── models/             # Data models
│   │   └── schemas.py      # Pydantic schemas
│   ├── utils/              # Utilities
│   │   └── sentiment.py    # Sentiment analysis
│   └── cli.py              # CLI interface
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── .github/                # GitHub configuration
│   └── workflows/          # CI/CD pipelines
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Project configuration
└── setup.py                # Package setup
```

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Main Endpoints

#### POST /api/search
Search for mentions across all sources.

**Request:**
```json
{
  "keyword": "cybersecurity",
  "google_results": 10,
  "twitter_results": 10,
  "reddit_results": 10,
  "news_results": 10,
  "enable_sentiment": true
}
```

**Response:**
```json
[
  {
    "id": "1",
    "source": "twitter",
    "keyword": "cybersecurity",
    "url": "https://twitter.com/...",
    "title": "Tweet about cybersecurity",
    "content": "...",
    "timestamp": "2024-01-01T12:00:00",
    "sentiment": "positive",
    "sentiment_confidence": 0.95
  }
]
```

#### GET /api/mentions
Retrieve stored mentions with filtering.

**Parameters:**
- `keyword`: Filter by keyword
- `source`: Filter by source (google, twitter, reddit, news)
- `start_date`: Start date (ISO 8601)
- `end_date`: End date (ISO 8601)
- `limit`: Max results (default: 100)
- `offset`: Pagination offset

#### GET /api/stats
Get statistics for collected mentions.

**Parameters:**
- `days`: Number of days to analyze (default: 7)

**Response:**
```json
{
  "total_mentions": 150,
  "by_source": {
    "twitter": 50,
    "google": 40,
    "reddit": 35,
    "news": 25
  },
  "by_sentiment": {
    "positive": 60,
    "neutral": 70,
    "negative": 20
  },
  "days": 7
}
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=osint_app

# Run specific test file
pytest tests/unit/test_models.py

# Run tests matching pattern
pytest -k "test_sentiment"

# Run with verbose output
pytest -v

# Generate HTML coverage report
pytest --cov=osint_app --cov-report=html
open htmlcov/index.html
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Format code (`black . && isort .`)
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is provided for educational and research purposes. Users are responsible for ensuring their use complies with all applicable laws and platform terms of service.

## ⚠️ Ethical Usage Notice

**This tool is intended for legitimate OSINT research and monitoring purposes only.**

Please ensure you:
- ✅ Use for legitimate research, brand monitoring, or security purposes
- ✅ Respect `robots.txt` and website terms of service
- ✅ Comply with data protection regulations (GDPR, CCPA, etc.)
- ✅ Rate-limit your requests to avoid overloading servers
- ✅ Only collect publicly available information
- ❌ Do NOT use for harassment, stalking, or illegal activities
- ❌ Do NOT scrape websites that explicitly prohibit it
- ❌ Do NOT violate platform terms of service

## 🆘 Support

- 📖 [Documentation](https://github.com/nrk8286/osint-app/wiki)
- 🐛 [Issue Tracker](https://github.com/nrk8286/osint-app/issues)
- 💬 [Discussions](https://github.com/nrk8286/osint-app/discussions)

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [Hugging Face Transformers](https://huggingface.co/transformers/)
- UI enhanced with [Rich](https://rich.readthedocs.io/)

---

**Remember**: With great power comes great responsibility. Use this tool ethically and legally.

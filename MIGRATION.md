## Migration Guide: v1.0 to v2.0

This guide helps you migrate from the basic OSINT monitor to the production-ready v2.0 platform.

### What's New in v2.0

The v2.0 platform is a complete rewrite with:
- **Modular architecture** instead of a single script
- **Async/await** for concurrent processing (3-5x faster)
- **Type safety** with Pydantic models
- **Database storage** with SQLite/PostgreSQL
- **Sentiment analysis** using AI models
- **REST API** with FastAPI
- **Enhanced CLI** with Rich formatting
- **Docker support** for easy deployment
- **Comprehensive tests** and CI/CD

### Backward Compatibility

**Good news:** Your existing code will continue to work! We've provided a compatibility wrapper.

#### Option 1: Keep Using the Old Interface

If you want to keep your existing code unchanged, simply use `osint_monitor_legacy.py`:

```bash
# Old way (still works)
python osint_monitor_legacy.py "keyword"
```

Or in your Python code:
```python
# Import from legacy module
from osint_monitor_legacy import OSINTMonitor

# Use exactly as before
monitor = OSINTMonitor()
mentions = monitor.collect_mentions(
    keyword="test",
    google_results=10,
    twitter_results=10
)
monitor.save_to_csv()
```

#### Option 2: Migrate to v2.0 (Recommended)

Migrating gives you access to all new features. Here's how:

**Before (v1.0):**
```python
from osint_monitor import OSINTMonitor

monitor = OSINTMonitor()
mentions = monitor.collect_mentions(
    keyword="cybersecurity",
    google_results=10,
    twitter_results=10
)
monitor.save_to_csv("results.csv")
```

**After (v2.0):**
```python
import asyncio
from osint_app.core.monitor import OSINTMonitor

# Async version (recommended)
async def main():
    monitor = OSINTMonitor(use_database=True, enable_sentiment=True)
    mentions = await monitor.collect_mentions(
        keyword="cybersecurity",
        google_results=10,
        twitter_results=10,
        reddit_results=10,  # New!
        news_results=10      # New!
    )
    monitor.save_to_json("results.json")  # JSON support!
    monitor.save_to_csv("results.csv")     # CSV still works

asyncio.run(main())

# Or use synchronous wrapper
from osint_app.core.monitor import collect_mentions_sync

mentions = collect_mentions_sync(
    keyword="cybersecurity",
    google_results=10
)
```

### API Changes

#### 1. Import Paths

| v1.0 | v2.0 |
|------|------|
| `from osint_monitor import OSINTMonitor` | `from osint_app.core.monitor import OSINTMonitor` |
| N/A | `from osint_app.models.schemas import Mention, SearchQuery` |
| N/A | `from osint_app.storage.database import DatabaseStorage` |

#### 2. Constructor Changes

**v1.0:**
```python
monitor = OSINTMonitor()
```

**v2.0:**
```python
monitor = OSINTMonitor(
    use_database=True,      # Optional: enable database storage
    enable_sentiment=True   # Optional: enable sentiment analysis
)
```

#### 3. Method Changes

**collect_mentions():**

v1.0:
```python
mentions = monitor.collect_mentions(
    keyword="test",
    google_results=10,
    twitter_results=10,
    scrape_urls=["https://example.com"]
)
```

v2.0 (async):
```python
mentions = await monitor.collect_mentions(
    keyword="test",
    google_results=10,
    twitter_results=10,
    reddit_results=10,    # New!
    news_results=10,      # New!
    enable_sentiment=True # New!
)
# Note: scrape_urls removed, use dedicated web source
```

#### 4. Data Structure Changes

**v1.0 returns dictionaries:**
```python
{
    'source': 'Twitter',
    'keyword': 'test',
    'url': 'https://...',
    'title': 'Tweet text',
    'timestamp': '2024-01-01T12:00:00',
    'content': '...'
}
```

**v2.0 returns Pydantic models:**
```python
Mention(
    source=SourceType.TWITTER,
    keyword='test',
    url='https://...',
    title='Tweet text',
    timestamp=datetime(...),
    content='...',
    sentiment=SentimentScore.POSITIVE,  # New!
    sentiment_confidence=0.95,           # New!
    author='username',                   # New!
    language='en',                       # New!
    metadata={...}                       # New!
)
```

To convert to dict: `mention.model_dump()`

### New Features You Should Use

#### 1. Database Storage

Instead of only CSV files, use the database:

```python
from osint_app.storage.database import DatabaseStorage

db = DatabaseStorage()

# Save mentions
db.save_mentions(mentions)

# Retrieve with filtering
recent = db.get_mentions(
    keyword="cybersecurity",
    start_date=datetime.now() - timedelta(days=7),
    limit=100
)

# Get statistics
stats = db.get_stats(days=30)
print(stats)
```

#### 2. Sentiment Analysis

```python
monitor = OSINTMonitor(enable_sentiment=True)

# Mentions will automatically include sentiment
mentions = await monitor.collect_mentions(
    keyword="product review",
    enable_sentiment=True
)

for mention in mentions:
    if mention.sentiment:
        print(f"{mention.title}: {mention.sentiment.value} ({mention.sentiment_confidence:.2f})")
```

#### 3. REST API

Start the API server:
```bash
uvicorn osint_app.api.main:app --reload
```

Use from any language:
```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "cybersecurity", "google_results": 10}'
```

#### 4. Enhanced CLI

```bash
# Beautiful rich-formatted output
osint-monitor "keyword" --output results.json

# Show statistics
osint-monitor --stats --days 30
```

#### 5. Docker Deployment

```bash
# Easy deployment with Docker
docker-compose up -d

# Access API at http://localhost:8000
```

### Configuration Migration

#### v1.0 Configuration

Only Twitter credentials in `.env`:
```bash
TWITTER_BEARER_TOKEN=...
```

#### v2.0 Configuration

Expanded `.env` with more options:
```bash
# Twitter
TWITTER_BEARER_TOKEN=...

# New data sources
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
NEWS_API_KEY=...

# Database
DB_URL=sqlite:///osint_data.db

# Features
ENABLE_SENTIMENT_ANALYSIS=true
ENABLE_CACHING=false

# API
API_PORT=8000
```

### Installation Changes

#### v1.0

```bash
pip install -r requirements.txt
```

#### v2.0

```bash
# Install with all features
pip install -r requirements.txt

# Or install as package
pip install -e .

# Then use command-line tools
osint-monitor "keyword"
osint-api  # starts API server
```

### Testing Your Migration

1. **Test backward compatibility:**
```bash
python osint_monitor_legacy.py "test"
```

2. **Test new platform:**
```bash
osint-monitor "test" --output test.json
```

3. **Test API:**
```bash
uvicorn osint_app.api.main:app --reload
# Visit http://localhost:8000/docs
```

### Step-by-Step Migration Checklist

- [ ] Back up existing `.env` file
- [ ] Copy `.env.example` to see new options
- [ ] Add new API credentials (Reddit, News API) if desired
- [ ] Update import statements in your code
- [ ] Convert synchronous code to async (or use wrapper)
- [ ] Update data structure handling (dict → Pydantic)
- [ ] Test with backward compatibility wrapper first
- [ ] Gradually migrate to new features
- [ ] Update requirements.txt in your projects
- [ ] Run tests: `pytest`
- [ ] Update documentation

### Troubleshooting

**Problem:** Import errors
```
ModuleNotFoundError: No module named 'osint_app'
```
**Solution:** Install the package: `pip install -e .`

**Problem:** Async errors
```
RuntimeError: asyncio.run() cannot be called from a running event loop
```
**Solution:** Use `await` in async functions or `collect_mentions_sync()` wrapper

**Problem:** Pydantic validation errors
```
ValidationError: 1 validation error for Mention
```
**Solution:** Check your data matches the schema or use `.model_dump()` to convert

**Problem:** Database locked errors
```
OperationalError: database is locked
```
**Solution:** Don't share database connections across threads. Use `get_session()` context manager.

### Getting Help

- Review the new README_v2.md for full documentation
- Check examples in `tests/` directory
- Use `--help` flag: `osint-monitor --help`
- Visit API docs: http://localhost:8000/docs
- Open an issue on GitHub

### Rollback Plan

If you need to rollback:

1. Keep using `osint_monitor_legacy.py`
2. Or checkout the old version:
```bash
git checkout v1.0
pip install -r requirements.txt
```

The legacy compatibility wrapper will be maintained for at least 6 months.

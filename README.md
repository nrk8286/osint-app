# OSINT App - Social Media Monitoring Tool

A simple yet powerful OSINT (Open Source Intelligence) application built in Python for monitoring social media mentions across multiple platforms, similar to Talkwalker.

## Features

- 🔍 **Multi-Platform Monitoring**: Track mentions across Twitter, Reddit, and general web sources
- 📊 **Sentiment Analysis**: Automatically analyze sentiment of mentions (positive, negative, neutral)
- 📈 **Engagement Metrics**: Track likes, shares, and comments for each mention
- 🎯 **Keyword Tracking**: Monitor multiple keywords simultaneously
- 📁 **Data Export**: Export results to JSON format
- 🎨 **Beautiful CLI**: Colorful command-line interface with formatted output
- 🔧 **Modular Design**: Easy to extend with additional platforms

## Installation

1. Clone the repository:
```bash
git clone https://github.com/nrk8286/osint-app.git
cd osint-app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Set up API credentials:
```bash
cp .env.example .env
# Edit .env with your API credentials
```

## Usage

### Command Line Interface

Basic usage:
```bash
python cli.py --keywords "Python" "AI" --platforms twitter reddit
```

Advanced options:
```bash
# Search with specific platforms
python cli.py -k "OpenAI" -p twitter --max-results 20

# Filter by sentiment
python cli.py -k "ChatGPT" --sentiment positive

# Export results to JSON
python cli.py -k "Machine Learning" --export results.json

# Quiet mode (summary only)
python cli.py -k "Python" --quiet

# Skip summary
python cli.py -k "Data Science" --no-summary
```

### Python API

```python
from osint_app.app import OSINTApp

# Initialize the app
app = OSINTApp()

# Search for mentions
mentions = app.search(
    keywords=['Python', 'AI'],
    platforms=['twitter', 'reddit', 'web'],
    max_results=100
)

# Get sentiment summary
sentiment = app.get_sentiment_summary()
print(f"Positive: {sentiment['positive']}")
print(f"Negative: {sentiment['negative']}")
print(f"Neutral: {sentiment['neutral']}")

# Filter by sentiment
positive_mentions = app.filter_by_sentiment('positive')

# Get platform distribution
platforms = app.get_platform_summary()

# Export results
results = app.export_results()
```

### Example Script

Run the example script to see all features:
```bash
python example.py
```

## Project Structure

```
osint-app/
├── osint_app/              # Main application package
│   ├── __init__.py         # Package initialization
│   ├── app.py              # Main OSINT app orchestrator
│   ├── models/             # Data models
│   │   └── __init__.py     # Mention and SearchQuery models
│   ├── monitors/           # Platform monitors
│   │   ├── __init__.py     # Monitor factory
│   │   ├── base.py         # Base monitor class
│   │   ├── twitter.py      # Twitter monitor
│   │   ├── reddit.py       # Reddit monitor
│   │   └── web.py          # Web scraping monitor
│   └── utils/              # Utility functions
│       └── __init__.py     # Sentiment analysis and text processing
├── cli.py                  # Command-line interface
├── example.py              # Example usage script
├── requirements.txt        # Python dependencies
├── config.example.json     # Example configuration file
├── .env.example            # Example environment variables
└── README.md               # This file
```

## Configuration

### API Credentials

To use real-time data from Twitter or Reddit APIs, you need to set up API credentials:

1. **Twitter API**: 
   - Sign up at [Twitter Developer Portal](https://developer.twitter.com/)
   - Create an app and get your API keys
   - Add keys to `.env` file

2. **Reddit API**:
   - Create an app at [Reddit Apps](https://www.reddit.com/prefs/apps)
   - Get your client ID and secret
   - Add credentials to `.env` file

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
```

## Demo Mode

The app works in **demo mode** by default without API credentials, generating sample data for demonstration purposes. This is perfect for testing and learning how the app works.

## Features in Detail

### Sentiment Analysis

Each mention is analyzed for sentiment using TextBlob:
- **Positive**: Sentiment polarity > 0.1
- **Negative**: Sentiment polarity < -0.1
- **Neutral**: Sentiment polarity between -0.1 and 0.1

### Engagement Metrics

Track engagement for each mention:
- **Likes**: Number of likes/favorites
- **Shares**: Number of retweets/shares
- **Comments**: Number of replies/comments
- **Total**: Sum of all engagement

### Platform Support

Current platforms:
- **Twitter**: Social media mentions and tweets
- **Reddit**: Posts and discussions
- **Web**: General web articles and blogs

Easy to extend with more platforms!

## CLI Options

```
usage: cli.py [-h] -k KEYWORDS [KEYWORDS ...] 
              [-p {twitter,reddit,web} [{twitter,reddit,web} ...]]
              [-m MAX_RESULTS] [-e EXPORT]
              [--sentiment {positive,negative,neutral}]
              [--no-summary] [--quiet]

options:
  -h, --help            Show help message
  -k, --keywords        Keywords to monitor (required)
  -p, --platforms       Platforms to monitor (default: all)
  -m, --max-results     Maximum results per platform (default: 100)
  -e, --export          Export results to JSON file
  --sentiment           Filter by sentiment
  --no-summary          Skip summary statistics
  --quiet               Only show summary
```

## Contributing

Contributions are welcome! To add a new platform monitor:

1. Create a new monitor class in `osint_app/monitors/`
2. Extend the `BaseMonitor` class
3. Implement `search()` and `monitor_keyword()` methods
4. Register the monitor in `osint_app/monitors/__init__.py`

## Dependencies

- `requests`: HTTP library for web scraping
- `beautifulsoup4`: HTML parsing
- `tweepy`: Twitter API wrapper
- `textblob`: Sentiment analysis
- `python-dotenv`: Environment variable management
- `colorama`: Colored terminal output
- `tabulate`: Pretty table formatting

## License

MIT License

## Author

OSINT App Team

## Acknowledgments

Inspired by professional OSINT tools like Talkwalker, but simplified for educational and personal use.

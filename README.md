# OSINT App - Social Media Monitoring Tool

A simple OSINT (Open Source Intelligence) application for monitoring social media mentions, similar to Talkwalker. This tool helps you track keywords across various sources including web search, news articles, and social media platforms.

## Features

- 🔍 **Multi-Source Collection**: Collect mentions from web search, news, and social media
- 📊 **Sentiment Analysis**: Automatic sentiment analysis of collected mentions using TextBlob
- 💾 **Data Storage**: Persistent storage using TinyDB
- 📈 **Statistics & Reports**: Generate comprehensive reports with sentiment breakdowns
- 🎨 **CLI Interface**: Easy-to-use command-line interface with colored output
- 🔧 **Extensible**: Modular architecture for adding new data sources

## Installation

1. Clone the repository:
```bash
git clone https://github.com/nrk8286/osint-app.git
cd osint-app
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys if you want to use social media APIs
```

## Usage

### Collect Mentions

Collect mentions for specific keywords from various sources:

```bash
python main.py collect -k "Python" -k "AI" -s web -s news -s social
```

Options:
- `-k, --keywords`: Keywords to monitor (can specify multiple)
- `-s, --sources`: Data sources to use (web, news, social)
- `-m, --max-results`: Maximum results per source (default: 10)

### List Collected Mentions

View collected mentions with various filters:

```bash
# List all mentions
python main.py list-mentions

# List mentions with filters
python main.py list-mentions --limit 10 --source twitter --sentiment positive
```

Options:
- `-l, --limit`: Number of mentions to show (default: 20)
- `-s, --source`: Filter by source (web_search, news, twitter, reddit)
- `-k, --keyword`: Filter by keyword
- `--sentiment`: Filter by sentiment (positive, negative, neutral)

### View Statistics

Display database statistics:

```bash
python main.py stats
```

### Generate Reports

Create comprehensive reports:

```bash
# Text report to console
python main.py report

# JSON report to file
python main.py report --format json --output report.json

# Text report to file
python main.py report --format text --output report.txt
```

Options:
- `-f, --format`: Report format (text, json)
- `-o, --output`: Output file path (optional)
- `-l, --limit`: Number of mentions to include (default: 100)

### View Configuration

Show current configuration:

```bash
python main.py config-info
```

### Clear Database

Remove all collected data:

```bash
python main.py clear
```

## Project Structure

```
osint-app/
├── osint_app/
│   ├── __init__.py
│   ├── cli.py                 # Command-line interface
│   ├── collectors/            # Data collection modules
│   │   ├── __init__.py
│   │   ├── base.py           # Base collector class
│   │   └── web_collector.py  # Web, news, and social media collectors
│   ├── analyzers/            # Analysis modules
│   │   ├── __init__.py
│   │   └── sentiment.py      # Sentiment analysis
│   ├── storage/              # Data storage
│   │   ├── __init__.py
│   │   └── database.py       # TinyDB wrapper
│   └── utils/                # Utility modules
│       ├── __init__.py
│       ├── config.py         # Configuration management
│       └── reporter.py       # Report generation
├── main.py                   # Main entry point
├── requirements.txt          # Python dependencies
├── .env.example             # Example environment configuration
├── .gitignore              # Git ignore file
└── README.md               # This file
```

## Architecture

### Collectors

The app uses a modular collector system:

- **BaseCollector**: Abstract base class for all collectors
- **WebSearchCollector**: Collects mentions from web search results
- **NewsCollector**: Collects mentions from news sources
- **SocialMediaCollector**: Collects mentions from social media platforms

### Sentiment Analysis

Uses TextBlob for sentiment analysis, providing:
- Polarity score (-1 to 1)
- Subjectivity score (0 to 1)
- Classification (positive, negative, neutral)

### Storage

TinyDB is used for lightweight, JSON-based storage with tables for:
- Mentions: All collected mentions with metadata
- Queries: History of search queries

## Example Workflow

1. **Collect data** for your brand or keywords:
```bash
python main.py collect -k "YourBrand" -k "YourProduct" -s web -s news -s social
```

2. **View statistics** to get an overview:
```bash
python main.py stats
```

3. **List mentions** to see what people are saying:
```bash
python main.py list-mentions --limit 20
```

4. **Filter by sentiment** to find issues or praise:
```bash
python main.py list-mentions --sentiment negative
```

5. **Generate a report** for stakeholders:
```bash
python main.py report --format text --output weekly_report.txt
```

## Future Enhancements

This is a basic OSINT tool. Here are potential enhancements:

- Integration with real social media APIs (Twitter, Reddit, Facebook)
- Integration with news APIs (NewsAPI, Google News)
- Advanced analytics (trending topics, influencer identification)
- Web dashboard for visualization
- Real-time monitoring and alerts
- Export to CSV/Excel
- Keyword tracking over time
- Geolocation analysis
- Multi-language support

## Dependencies

- **requests**: HTTP library for web requests
- **beautifulsoup4**: HTML parsing
- **python-dotenv**: Environment variable management
- **pandas**: Data manipulation
- **textblob**: Natural language processing and sentiment analysis
- **click**: CLI framework
- **colorama**: Colored terminal output
- **tinydb**: Lightweight JSON database

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Disclaimer

This tool is for educational and legitimate OSINT purposes only. Always respect:
- Terms of Service of the platforms you're monitoring
- Privacy laws and regulations
- Rate limits and API guidelines
- Ethical data collection practices

## Support

For issues, questions, or contributions, please open an issue on GitHub.

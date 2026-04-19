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
# OSINT Social Media Monitoring App

A Python-based Open Source Intelligence (OSINT) tool for monitoring keyword mentions across multiple platforms, inspired by Talkwalker. This application aggregates mentions from Google searches, Twitter API, and custom websites, providing a simple yet powerful solution for social media monitoring and brand tracking.

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

**Users are responsible for ensuring their use complies with all applicable laws and regulations.**

## Features

- 🔍 **Google Search Integration**: Collect keyword mentions from Google search results
- 🐦 **Twitter API Integration**: Monitor tweets containing specific keywords
- 🌐 **Web Scraping**: Scrape custom websites for keyword mentions
- 💾 **CSV Export**: Save all collected mentions to CSV for analysis
- 🔒 **Secure Configuration**: API keys managed via environment variables
- ⚡ **Rate Limiting**: Built-in delays to respect server resources
- 📊 **Structured Data**: Organized mention data with source, timestamp, and content

## Prerequisites

- Python 3.7 or higher
- Twitter Developer Account (for Twitter API access)
- Internet connection

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/nrk8286/osint-app.git
cd osint-app
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

#### Twitter API Setup

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a new project and app
3. Generate your API credentials:
   - API Key
   - API Secret
   - Access Token
   - Access Token Secret
   - Bearer Token

#### Environment Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Twitter API credentials:
   ```
   TWITTER_API_KEY=your_actual_api_key
   TWITTER_API_SECRET=your_actual_api_secret
   TWITTER_ACCESS_TOKEN=your_actual_access_token
   TWITTER_ACCESS_TOKEN_SECRET=your_actual_access_token_secret
   TWITTER_BEARER_TOKEN=your_actual_bearer_token
   ```

**Note**: Keep your `.env` file secure and never commit it to version control (it's already in `.gitignore`).

## Usage

### Basic Usage

Run the monitor with a keyword:

```bash
python osint_monitor.py "your keyword"
```

Or run interactively:

```bash
python osint_monitor.py
# Enter keyword when prompted
```

### Example

```bash
python osint_monitor.py "artificial intelligence"
```

This will:
1. Search Google for "artificial intelligence"
2. Search Twitter for recent tweets mentioning "artificial intelligence"
3. (Optional) Scrape configured websites for mentions
4. Save all results to a timestamped CSV file (e.g., `mentions_20231029_143022.csv`)

### Customizing Web Scraping

To add custom websites to scrape, edit the `scrape_urls` list in `osint_monitor.py`:

```python
scrape_urls = [
    'https://example.com',
    'https://news.ycombacker.com',
    # Add more URLs here
]
```

## Output

The application generates a CSV file with the following columns:

- **source**: Platform where mention was found (Google, Twitter, Web Scraping)
- **keyword**: The searched keyword
- **url**: Link to the mention
- **title**: Title or description of the mention
- **timestamp**: When the mention was collected
- **content**: Actual content of the mention (if available)

Example output filename: `mentions_20231029_143022.csv`

## Dependencies

- **googlesearch-python**: For Google search integration
- **tweepy**: Twitter API client
- **requests**: HTTP library for web scraping
- **beautifulsoup4**: HTML parsing for web scraping
- **pandas**: Data manipulation and CSV export
- **python-dotenv**: Environment variable management

## Troubleshooting

### Google Search Issues

If you encounter rate limiting or blocking from Google:
- Reduce the number of results requested
- Increase sleep intervals between requests
- Use Google's Custom Search API for production use

### Twitter API Issues

Common issues:
- **Authentication Error**: Check your credentials in `.env`
- **Rate Limit**: Twitter has rate limits; wait before making more requests
- **Insufficient Access**: Ensure your Twitter Developer account has appropriate access level

### Web Scraping Issues

- Some websites may block automated scraping
- Always check and respect `robots.txt`
- Consider using official APIs when available

## Limitations

- **Google Search**: Uses unofficial API, may have rate limits
- **Twitter API**: Free tier has limited requests and 7-day search history
- **Web Scraping**: Some sites actively block scraping; respect their policies

## Contributing

Contributions are welcome! Please ensure your contributions:
- Follow ethical OSINT practices
- Include appropriate error handling
- Maintain code quality and documentation
- Respect privacy and legal boundaries

## License

This project is provided for educational and research purposes. Users are responsible for ensuring their use complies with all applicable laws and platform terms of service.

## Disclaimer

This tool is provided "as is" without warranty of any kind. The authors are not responsible for any misuse or damage caused by this tool. Always ensure your monitoring activities comply with applicable laws and regulations.

## Resources

- [OSINT Framework](https://osintframework.com/)
- [Twitter API Documentation](https://developer.twitter.com/en/docs)
- [Google Custom Search API](https://developers.google.com/custom-search)
- [Beautiful Soup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review Twitter API and other service documentation

---

**Remember**: With great power comes great responsibility. Use this tool ethically and legally.

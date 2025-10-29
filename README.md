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

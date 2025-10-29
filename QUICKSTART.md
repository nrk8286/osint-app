# Quick Start Guide

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/nrk8286/osint-app.git
cd osint-app

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure Twitter API (optional but recommended)
cp .env.example .env
# Edit .env and add your Twitter API credentials
```

## Basic Usage

### Interactive Mode
```bash
python osint_monitor.py
# Enter keyword when prompted
```

### Command Line Mode
```bash
python osint_monitor.py "your search term"
```

### Example Searches
```bash
# Monitor a brand
python osint_monitor.py "YourBrand"

# Track a topic
python osint_monitor.py "artificial intelligence"

# Security monitoring
python osint_monitor.py "data breach 2024"
```

## Output

Results are saved to a CSV file named `mentions_TIMESTAMP.csv` with columns:
- **source**: Where the mention was found (Google, Twitter, Web)
- **keyword**: Search term used
- **url**: Link to the mention
- **title**: Title/description
- **timestamp**: When collected
- **content**: Actual mention content

## Programmatic Usage

```python
from osint_monitor import OSINTMonitor

# Initialize
monitor = OSINTMonitor()

# Collect mentions
mentions = monitor.collect_mentions(
    keyword="cybersecurity",
    google_results=10,
    twitter_results=10
)

# Save to CSV
monitor.save_to_csv("results.csv")
```

## Twitter API Setup

1. Go to https://developer.twitter.com/
2. Create a project and app
3. Generate credentials:
   - API Key
   - API Secret  
   - Access Token
   - Access Token Secret
   - Bearer Token
4. Add to `.env` file

## Tips

- Start with small result counts to test
- Respect rate limits - add delays between searches
- Use specific keywords for better results
- Check CSV output format before large-scale collection

## Troubleshooting

**No Twitter results?**
- Check your `.env` credentials
- Verify Twitter Developer account status
- Check rate limits

**Google blocked?**
- Reduce search frequency
- Add more delays
- Consider Google Custom Search API

**Web scraping errors?**
- Some sites block automated access
- Check robots.txt
- Use official APIs when available

## Legal & Ethical

⚠️ **IMPORTANT**: 
- Only use for legitimate purposes
- Respect website terms of service
- Comply with all applicable laws
- Only collect public information

## Support

- See full documentation in README.md
- Check CONTRIBUTING.md for development
- Open GitHub issues for bugs

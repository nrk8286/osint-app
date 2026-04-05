# Twitter API Setup Guide

This guide walks you through setting up Twitter API access for the OSINT Monitor app.

## Why Twitter API?

With Twitter API integration, you can:
- 🔍 Search for mentions of keywords, emails, or usernames
- 📊 Track recent tweets about your target
- 👥 Find user interactions and engagement
- 📈 Monitor trending topics
- 🔎 Discover related accounts and hashtags
- ⏰ Get timestamps of when mentions occurred

## Step 1: Create a Twitter Developer Account

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Click **"Sign up"** or **"Sign in"** with your Twitter account
3. If you don't have a Twitter account, create one first at [twitter.com](https://twitter.com)

## Step 2: Create a Project & App

1. In the Developer Portal, click **"Create Project"**
2. Give your project a name (e.g., "OSINT Monitor")
3. Select use case: **"Research"** or **"Other"**
4. Describe your use case:
   ```
   Academic research and OSINT (Open Source Intelligence) 
   for social media monitoring and brand tracking.
   ```
5. Click through the remaining steps
6. Once project is created, click **"Create App"**
7. Name your app (e.g., "osint-monitor")
8. Review the terms and create the app

## Step 3: Generate API Keys

### Get Your Credentials

1. In your app settings, go to **"Keys and Tokens"** tab
2. Generate/view the following:

#### API Key (API Key)
- Click **"Regenerate"** next to "API Key"
- Copy the value → save it somewhere safe

#### API Secret (API Secret Key)
- Click **"Regenerate"** next to "API Key Secret"
- Copy the value → save it somewhere safe

#### Access Token
- Click **"Generate"** under "Access Token & Secret"
- Copy the "Access Token" → save it

#### Access Token Secret
- Copy the "Access Token Secret" → save it

#### Bearer Token
- Scroll down to find "Bearer Token"
- Copy the value → save it

**⚠️ Important:** Never share these tokens or commit them to GitHub!

## Step 4: Enable Required Permissions

1. Go to **"App settings"** tab
2. Scroll to **"Authentication settings"**
3. Make sure **"OAuth 2.0"** is enabled
4. Set **"App only authentication"** to enabled (for bearer token)
5. Go to **"User Authentication settings"**
6. Enable **"Read and Write"** or **"Read"** permissions (minimum)
7. Set Callback URL to `http://localhost:8000` (for testing)

## Step 5: Configure .env File

1. In your project directory, copy the example:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```bash
   # Twitter API Credentials
   # Get these from https://developer.twitter.com/
   TWITTER_API_KEY=your_actual_api_key_here
   TWITTER_API_SECRET=your_actual_api_secret_here
   TWITTER_ACCESS_TOKEN=your_actual_access_token_here
   TWITTER_ACCESS_TOKEN_SECRET=your_actual_access_token_secret_here
   TWITTER_BEARER_TOKEN=your_actual_bearer_token_here
   ```

3. **Save the file**

4. Make sure `.env` is in `.gitignore` (it should be by default):
   ```bash
   cat .gitignore | grep ".env"
   ```

## Step 6: Test Your Configuration

### Verify the Setup

```bash
python3 << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

print("Checking Twitter API configuration...")
print()

keys = [
    'TWITTER_API_KEY',
    'TWITTER_API_SECRET', 
    'TWITTER_ACCESS_TOKEN',
    'TWITTER_ACCESS_TOKEN_SECRET',
    'TWITTER_BEARER_TOKEN'
]

configured = True
for key in keys:
    value = os.getenv(key)
    if value and value != f"your_{key.lower()}_here":
        status = "✅"
    else:
        status = "❌"
        configured = False
    print(f"{status} {key}: {'Configured' if value else 'Missing'}")

print()
if configured:
    print("✅ All Twitter API credentials are configured!")
else:
    print("❌ Please add your Twitter API credentials to .env")
EOF
```

### Test with OSINT Monitor

```bash
python osint_monitor.py "nrk8286"
```

You should see Twitter searches working!

## Troubleshooting

### Error: "Twitter credentials not found"

1. Check that `.env` file exists in the project root
2. Verify the file contains all 5 keys
3. Make sure you used the exact variable names from `.env.example`
4. Restart Python (environment variables are loaded on startup)

### Error: "Authentication failed"

1. Verify your Bearer Token is correct
2. Check if your Twitter Developer account is still active
3. Ensure you haven't hit API rate limits
4. Try regenerating your tokens

### Error: "Insufficient access"

1. Go to Twitter Developer Portal → Your App
2. Check **"Elevated"** or **"Pro"** access level
3. Some features require elevated access
4. Apply for elevated access if needed

### Rate Limiting Issues

Twitter API has rate limits:
- **Free tier**: 300 requests per 15 minutes
- **Academic**: 2 million tweets per month

If you hit rate limits, the app will:
1. Show a rate limit message
2. Wait for the limit to reset
3. Retry the request

You can configure this in `osint_monitor.py` if needed.

## API Pricing & Tiers

### Free Tier (Includes)
- 300 requests per 15-minute window
- Search recent tweets (7-day lookback)
- Basic tweet fields
- Good for: Testing and light research

### Academic Research
- 2 million tweets per month
- Full archive access
- Extended fields
- Free for students/researchers
- Apply at: https://developer.twitter.com/en/products/twitter-api/academic-research

### Pro/Paid Plans
- Higher rate limits
- Priority support
- Custom features

## Security Best Practices

### ✅ DO:
- Store credentials in `.env` file
- Add `.env` to `.gitignore`
- Rotate tokens periodically
- Use minimal required permissions
- Monitor for unauthorized access
- Regenerate tokens if compromised

### ❌ DON'T:
- Commit `.env` to GitHub
- Share your tokens publicly
- Hard-code credentials in Python files
- Use the same tokens for multiple apps
- Give unnecessary API permissions
- Leave old apps active

## Using Twitter API with OSINT Monitor

### Basic Search
```python
from osint_monitor import OSINTMonitor

monitor = OSINTMonitor()

# Search for mentions
results = monitor.collect_mentions(
    keyword="nrk8286",
    google_results=10,
    twitter_results=50,  # Get 50 tweets
    scrape_urls=[],
    use_recon_ng=False
)

monitor.save_to_csv()
```

### Advanced Search
```python
# Only Twitter search
twitter_mentions = monitor.search_twitter("nrk8286", max_results=100)

# Filter results
recent_tweets = [m for m in twitter_mentions if 'Twitter' in m['source']]

print(f"Found {len(recent_tweets)} recent tweets")
```

### Search Operators
You can use Twitter operators in your search:

```python
# Find tweets from specific user
monitor.search_twitter('from:nrk8286', max_results=50)

# Find mentions
monitor.search_twitter('mentions:nrk8286', max_results=50)

# Find with hashtags
monitor.search_twitter('#OSINT #security', max_results=50)

# Exclude retweets
monitor.search_twitter('nrk8286 -is:retweet', max_results=50)
```

## Next Steps

1. ✅ Create Twitter Developer account
2. ✅ Generate API credentials
3. ✅ Add credentials to `.env`
4. ✅ Test with OSINT Monitor
5. ✅ Run your first investigation
6. ✅ (Optional) Apply for Academic Research access

## Resources

- **Twitter API Docs**: https://developer.twitter.com/en/docs
- **API Reference**: https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query
- **Rate Limits**: https://developer.twitter.com/en/docs/projects/overview#rate-limits
- **Academic Research**: https://developer.twitter.com/en/products/twitter-api/academic-research

## Support

Having issues?
- Check [Twitter API Documentation](https://developer.twitter.com/en/docs)
- Review [Common Issues](https://developer.twitter.com/en/support/troubleshooting)
- Open an issue on the [OSINT Monitor repository](https://github.com/nrk8286/osint-app)

---

**Remember:** Your Twitter credentials are sensitive. Keep them secure and never share them!

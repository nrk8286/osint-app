# Complete OSINT Monitor Setup Guide

Complete guide to setting up all features of the OSINT Monitor application.

## 📋 Overview

This guide covers:
1. ✅ Basic Installation
2. ✅ Twitter API Configuration
3. ✅ Recon-ng Framework
4. ✅ Web Scraping Setup
5. ✅ Running Investigations

## 1️⃣ Basic Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Git
- Internet connection

### Install Dependencies

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/nrk8286/osint-app.git
cd osint-app

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

✅ **Basic setup complete!** You can now use Google and web scraping features.

---

## 2️⃣ Twitter API Setup (5 minutes)

### Quick Setup

```bash
# Interactive setup assistant
python setup_twitter_api.py
```

This will guide you through:
1. Creating Twitter Developer account
2. Generating API credentials
3. Configuring .env file
4. Testing the connection

### Manual Setup

1. **Get Twitter API Credentials:**
   - Visit: https://developer.twitter.com/en/portal/dashboard
   - Create a project and app
   - Generate API keys and bearer token

2. **Configure .env File:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your credentials:
   ```
   TWITTER_API_KEY=your_api_key
   TWITTER_API_SECRET=your_api_secret
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
   TWITTER_BEARER_TOKEN=your_bearer_token
   ```

3. **Verify Configuration:**
   ```bash
   python setup_twitter_api.py --validate
   ```

4. **Test Connection:**
   ```bash
   python setup_twitter_api.py --test
   ```

✅ **Twitter API ready!**

---

## 3️⃣ Recon-ng Framework Setup (10 minutes)

### Install Recon-ng

```bash
# Clone recon-ng repository
git clone https://github.com/lanmaster53/recon-ng.git
cd recon-ng

# Install dependencies
pip install -r requirements.txt

# Create symlink for easy access (optional)
sudo ln -s $(pwd)/recon-ng /usr/local/bin/recon-ng

# Or add to PATH in ~/.bashrc or ~/.zshrc
export PATH="$PATH:/path/to/recon-ng"

# Return to osint-app directory
cd ../osint-app
```

### Verify Installation

```bash
recon-ng -v
```

Should show version number like: `5.x.x`

### Optional: Configure API Keys

For enhanced email harvesting and reconnaissance:

```bash
recon-ng

# Inside recon-ng shell (interactive):
set HUNTER_API_KEY your_key
set SHODAN_API_KEY your_key
exit
```

API providers to consider:
- **Hunter.io** - Email discovery
- **Shodan** - Infrastructure/IP intelligence
- **Clearbit** - Company and person data

✅ **Recon-ng ready!**

---

## 4️⃣ Web Scraping Configuration

### Basic Setup

The web scraping functionality is already built-in. You just need to configure URLs to scrape.

### Example: Add Target URLs

Edit a Python script:

```python
from osint_monitor import OSINTMonitor

monitor = OSINTMonitor()

# Search with web scraping enabled
results = monitor.collect_mentions(
    keyword="nrk8286",
    google_results=10,
    twitter_results=10,
    scrape_urls=[
        "https://github.com/search?q=nrk8286",
        "https://stackoverflow.com/search?q=nrk8286",
        # Add more URLs to scrape
    ],
    use_recon_ng=False
)

monitor.save_to_csv()
```

### Best Practices

- ✅ Only scrape websites you have permission to access
- ✅ Respect `robots.txt` and terms of service
- ✅ Use reasonable delays between requests
- ✅ Identify your requests with User-Agent
- ✅ Don't overload servers

---

## 5️⃣ Running Your First Investigation

### Option A: Interactive Mode

```bash
python osint_monitor.py

# Enter keyword when prompted
```

### Option B: Command Line

```bash
python osint_monitor.py "nrk8286"
```

### Option C: Advanced Python Script

```bash
python3 << 'EOF'
from osint_monitor import OSINTMonitor

monitor = OSINTMonitor()

# Comprehensive investigation
results = monitor.collect_mentions(
    keyword="nrk8286",
    google_results=20,
    twitter_results=50,
    scrape_urls=["https://github.com/nrk8286"],
    use_recon_ng=True  # If Recon-ng is installed
)

# Get summary
print(f"\nTotal results: {len(results)}")

# View by source
sources = {}
for r in results:
    src = r.get('source', 'Unknown')
    sources[src] = sources.get(src, 0) + 1

print("\nBreakdown:")
for source, count in sorted(sources.items()):
    print(f"  {source}: {count}")

# Save to CSV
monitor.save_to_csv()

# View results
print(f"\n✅ Results saved to mentions_*.csv")
EOF
```

### View Results

The app generates CSV files with naming pattern: `mentions_YYYYMMDD_HHMMSS.csv`

Open in Excel, Google Sheets, or command line:

```bash
cat mentions_*.csv | head -20
```

---

## 🎯 Quick Reference

### Troubleshooting

| Issue | Solution |
|-------|----------|
| "Twitter credentials not found" | Run: `python setup_twitter_api.py` |
| "Google search returns 0 results" | Google Search is rate-limited; try Twitter API instead |
| "recon-ng not found" | Install recon-ng and add to PATH |
| ".env file not found" | Copy .env.example to .env and add credentials |

### Common Tasks

**Search for a username:**
```bash
python osint_monitor.py "username"
```

**Search for an email:**
```bash
python osint_monitor.py "user@example.com"
```

**Domain reconnaissance:**
```python
from osint_monitor import OSINTMonitor
monitor = OSINTMonitor()
results = monitor.recon_domain("example.com")
```

**Email harvesting:**
```python
emails = monitor.harvest_emails("example.com")
```

**Batch processing:**
```python
targets = ["target1.com", "target2.com", "target3.com"]
for target in targets:
    monitor.collect_mentions(target, use_recon_ng=True)
monitor.save_to_csv()
```

---

## 📚 Feature Matrix

| Feature | Status | Setup Required |
|---------|--------|-----------------|
| Google Search | ✅ | None |
| Twitter API | ✅ | Twitter API keys |
| Web Scraping | ✅ | None |
| Recon-ng | ✅ | Recon-ng install |
| Email Harvesting | ✅ | Recon-ng + optional APIs |
| Domain Enumeration | ✅ | Recon-ng |
| CSV Export | ✅ | None |

---

## 🔒 Security Checklist

- [ ] .env file is in .gitignore
- [ ] Never commit .env to GitHub
- [ ] API keys are unique and rotated
- [ ] Only using public information
- [ ] Respecting rate limits
- [ ] Using respectful User-Agent headers
- [ ] Complying with ToS of all services
- [ ] Following local laws

---

## 📖 Complete Documentation

For more details, see:

- [README.md](README.md) - Project overview
- [TWITTER_API_SETUP.md](TWITTER_API_SETUP.md) - Twitter API details
- [RECON_NG_SETUP.md](RECON_NG_SETUP.md) - Recon-ng setup
- [RECON_NG_QUICKSTART.md](RECON_NG_QUICKSTART.md) - Recon-ng examples
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide

---

## 🚀 Next Steps

1. ✅ Run basic installation
2. ✅ Set up Twitter API (optional but recommended)
3. ✅ Install Recon-ng (optional for advanced features)
4. ✅ Run your first investigation
5. ✅ Explore the CSV results
6. ✅ Integrate into your workflow

---

## 💬 Need Help?

- Check the documentation files above
- Review the example scripts
- Run: `python recon_ng_examples.py`
- Open an issue on GitHub

---

**Remember:** Use ethically and legally! 🙏

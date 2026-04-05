# Recon-ng Quick Start Guide

Get started with Recon-ng integration in 5 minutes!

## 1. Install Recon-ng

```bash
# Clone and install
git clone https://github.com/lanmaster53/recon-ng.git
cd recon-ng
pip install -r requirements.txt

# Or use the symlink method for easier access
sudo ln -s $(pwd)/recon-ng /usr/local/bin/recon-ng
```

## 2. Verify Installation

```bash
recon-ng -v
# Should show version like: 5.x.x
```

## 3. Test with OSINT Monitor

```bash
# Simple domain reconnaissance
python osint_monitor.py "example.com"

# Enable Recon-ng features (modify osint_monitor.py to set use_recon_ng=True)
```

## 4. Use in Python

```python
from osint_monitor import OSINTMonitor

monitor = OSINTMonitor()

# Domain reconnaissance
results = monitor.recon_domain("example.com")

# Email harvesting
emails = monitor.harvest_emails("example.com")

# Save results
monitor.save_to_csv()
```

## 5. Common Recon-ng Tasks

### Enumerate Subdomains

```python
from recon_ng_wrapper import ReconNgWrapper

recon = ReconNgWrapper()
results = recon.enumerate_domain("example.com")
```

### Harvest Emails

```python
emails = recon.harvest_emails("example.com")
for email in emails:
    print(email['value'])
```

### Check Available Modules

```bash
recon-ng --modules
```

## Common Modules

| Task | Module |
|------|--------|
| Find subdomains | `recon/domains-hosts/dns_subdomain_enum` |
| Get SSL certs | `recon/domains-hosts/ssl_certificate_enum` |
| WHOIS lookup | `recon/domains-companies/whois_companies` |
| Find emails | `recon/companies-contacts/hunter` |

## Optimization Tips

### Add API Keys (Optional)

```bash
recon-ng
# In shell:
set HUNTER_API_KEY your_key
set SHODAN_API_KEY your_key
```

### Improve Email Discovery

Email harvesting works better with API keys from:
- Hunter.io
- RocketReach
- Clearbit

## Troubleshooting

**Problem**: "recon-ng not found"
- Solution: Add to PATH or use full path `/path/to/recon-ng/recon-ng`

**Problem**: "Module not found"
- Solution: Check module name with `recon-ng --modules`

**Problem**: "Authentication failed"
- Solution: Configure API keys (optional but recommended)

## Next Steps

1. Read the full [RECON_NG_SETUP.md](RECON_NG_SETUP.md) guide
2. Check [Recon-ng Wiki](https://github.com/lanmaster53/recon-ng/wiki)
3. Explore available modules
4. Configure API keys for better results
5. Use in your OSINT workflow!

---

**Pro Tip**: Combine Recon-ng with Google, Twitter, and web scraping for comprehensive OSINT coverage!

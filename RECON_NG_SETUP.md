# Recon-ng Integration Setup Guide

This guide explains how to install and configure Recon-ng for use with the OSINT Monitor app.

## What is Recon-ng?

Recon-ng is a powerful reconnaissance framework designed for OSINT. It provides modules for:

- **Domain Reconnaissance**: WHOIS, DNS, SSL certificate enumeration
- **Email Harvesting**: Email discovery from various sources
- **Subdomain Enumeration**: Find subdomains of target domains
- **Company Information**: Gather intelligence on companies
- **Contact Information**: Locate and verify contact details
- **Social Media Profiling**: Research on social platforms
- **And much more!**

## Installation

### Prerequisites

- Python 3.7+
- Git
- Linux/macOS or WSL2 on Windows

### Step 1: Install Recon-ng

#### Option A: From GitHub (Recommended)

```bash
# Clone the recon-ng repository
git clone https://github.com/lanmaster53/recon-ng.git
cd recon-ng

# Install dependencies
pip install -r requirements.txt

# Create a symlink for easy access (optional)
sudo ln -s $(pwd)/recon-ng /usr/local/bin/recon-ng
# Or add to PATH in ~/.bashrc or ~/.zshrc:
# export PATH="$PATH:/path/to/recon-ng"
```

#### Option B: From PyPI (if available)

```bash
pip install recon-ng
```

### Step 2: Verify Installation

```bash
recon-ng -v
```

You should see the version number if installed correctly.

### Step 3: Configure API Keys (Optional but Recommended)

Recon-ng works best with API keys from various services. Configure them:

```bash
# Start recon-ng
recon-ng

# Inside recon-ng shell:
# Add API keys for enhanced functionality
set SHODAN_API_KEY your_api_key
set TWITTER_API_KEY your_api_key
set LINKEDIN_API_KEY your_api_key
```

Common API sources:
- **Shodan**: https://shodan.io/ (Domain/IP reconnaissance)
- **Twitter API**: https://developer.twitter.com/ (Social media research)
- **LinkedIn**: https://www.linkedin.com/developers/ (Company/person research)
- **Hunter.io**: https://hunter.io/ (Email harvesting)

## Usage with OSINT Monitor

### Basic Usage

Once installed, the OSINT Monitor will automatically detect and initialize Recon-ng.

```bash
# For domain reconnaissance
python osint_monitor.py "example.com" --recon-ng
```

### Using Python API

```python
from osint_monitor import OSINTMonitor

# Initialize monitor
monitor = OSINTMonitor()

# Collect mentions with Recon-ng enabled
mentions = monitor.collect_mentions(
    keyword="example.com",
    google_results=10,
    twitter_results=10,
    use_recon_ng=True  # Enable Recon-ng
)

# Save results
monitor.save_to_csv()
```

### Available Recon-ng Methods

#### Domain Reconnaissance

```python
# Enumerate a domain (subdomains, SSL certs, WHOIS info)
results = monitor.recon_domain("example.com")
```

#### Email Harvesting

```python
# Harvest emails associated with a domain
emails = monitor.harvest_emails("example.com")
```

## Recon-ng Module Examples

Common useful modules:

| Module | Purpose |
|--------|---------|
| `recon/domains-hosts/dns_subdomain_enum` | Enumerate subdomains |
| `recon/domains-hosts/ssl_certificate_enum` | Extract SSL certificate info |
| `recon/domains-companies/whois_companies` | WHOIS lookups |
| `recon/companies-contacts/linkedin_linkedin` | LinkedIn company research |
| `recon/contacts-credentials/haveibeenpwned` | Check compromised passwords |
| `recon/phones-profiles/twitter_phones` | Find Twitter profiles by phone |

View all modules:

```bash
recon-ng --modules
```

## Troubleshooting

### Recon-ng not found

If you get "recon-ng not available":

1. Verify installation:
   ```bash
   which recon-ng
   recon-ng -v
   ```

2. Add to PATH if needed:
   ```bash
   export PATH="$PATH:/path/to/recon-ng"
   ```

3. Check Python path if installed as module:
   ```bash
   python -c "import recon_ng; print(recon_ng.__path__)"
   ```

### API Key Issues

Some modules require API keys. If you get authentication errors:

1. Check your API keys are set correctly
2. Ensure the API service hasn't revoked access
3. Verify you have sufficient API quota

### Module Execution Timeout

If a module is timing out:

1. Check your internet connection
2. Try a simpler module first
3. Reduce the workload (fewer domains, etc.)
4. Increase timeout in `recon_ng_wrapper.py` if needed

### Workspace Issues

If you see workspace errors:

```bash
# List existing workspaces
recon-ng --workspaces

# Delete problematic workspace
recon-ng -w workspace_name --delete --no-prompt
```

## Best Practices

### Ethical Usage

- Only use Recon-ng on domains/systems you own or have permission to test
- Respect rate limits of external APIs
- Follow local laws and regulations
- Document your activities for compliance
- Use for legitimate OSINT and security research only

### Performance Tips

1. **Batch Processing**: Process multiple domains efficiently
   ```python
   domains = ["example.com", "test.com", "demo.com"]
   for domain in domains:
       monitor.recon_domain(domain)
   ```

2. **API Key Configuration**: Set up API keys for faster results

3. **Workspace Management**: Clean up old workspaces to avoid clutter
   ```bash
   recon-ng -w old_workspace --delete --no-prompt
   ```

4. **Module Selection**: Use only modules you need to save time

### Security Tips

- Store API keys in `.env` file (not in code)
- Never commit credentials to version control
- Rotate API keys regularly
- Use restricted API scopes when available
- Monitor API usage for anomalies

## Output Format

Recon-ng results are formatted consistently:

```python
{
    'source': 'Recon-ng',
    'type': 'subdomain',  # or 'certificate', 'whois', 'email', etc.
    'domain': 'example.com',
    'module': 'recon/domains-hosts/dns_subdomain_enum',
    'output': 'result_data',
    'timestamp': '2024-01-15T10:30:45.123456'
}
```

## Advanced Usage

### Custom Module Execution

For advanced users, directly interact with the wrapper:

```python
from recon_ng_wrapper import ReconNgWrapper

recon = ReconNgWrapper()

if recon.is_available():
    # Run a specific module
    result = recon.run_module(
        workspace="my_workspace",
        module="recon/domains-hosts/dns_subdomain_enum",
        options={"SOURCE": "example.com"}
    )
    print(result)
```

### Batch Domain Processing

```python
from osint_monitor import OSINTMonitor

monitor = OSINTMonitor()
domains = ["example.com", "test.org", "demo.net"]

all_results = []
for domain in domains:
    results = monitor.collect_mentions(
        keyword=domain,
        use_recon_ng=True
    )
    all_results.extend(results)

monitor.save_to_csv()
```

## Resources

- **Official Recon-ng Wiki**: https://github.com/lanmaster53/recon-ng/wiki
- **Module Documentation**: https://github.com/lanmaster53/recon-ng/wiki/Module-Index
- **OSINT Framework**: https://osintframework.com/
- **OSINT Techniques**: https://www.osinttechniques.com/

## Support

For issues specific to:

- **Recon-ng**: Check the [GitHub Issues](https://github.com/lanmaster53/recon-ng/issues)
- **OSINT Monitor**: Open an issue in the [project repository](https://github.com/nrk8286/osint-app)
- **Integration**: See the CONTRIBUTING.md file

---

**Remember**: Use Recon-ng ethically and legally. Always obtain proper authorization before conducting reconnaissance on any systems or domains you do not own.

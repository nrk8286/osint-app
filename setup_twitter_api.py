#!/usr/bin/env python3
"""
Interactive Twitter API Configuration Setup
Helps you set up and validate Twitter API credentials for OSINT Monitor
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv


def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def check_env_file():
    """Check if .env file exists"""
    env_path = Path('.env')
    return env_path.exists()


def create_env_file():
    """Create .env file from template"""
    print_header("Creating .env File")

    if os.path.exists('.env'):
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("Cancelled. Using existing .env file.")
            return True

    try:
        with open('.env', 'w') as f:
            f.write("""# Twitter API Credentials
# Get these from https://developer.twitter.com/
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here
""")
        print("✅ Created .env file")
        print("   Edit the file with your Twitter API credentials")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False


def validate_credentials():
    """Validate configured credentials"""
    print_header("Validating Twitter API Credentials")

    # Load environment variables
    load_dotenv()

    keys = {
        'TWITTER_API_KEY': 'API Key',
        'TWITTER_API_SECRET': 'API Secret',
        'TWITTER_ACCESS_TOKEN': 'Access Token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'Access Token Secret',
        'TWITTER_BEARER_TOKEN': 'Bearer Token (Required)',
    }

    all_valid = True
    configured_count = 0

    for env_key, display_name in keys.items():
        value = os.getenv(env_key)

        if not value or value.startswith('your_'):
            print(f"❌ {display_name:.<40} NOT CONFIGURED")
            all_valid = False
        else:
            # Show masked value
            masked = value[:10] + '***' + value[-4:] if len(value) > 14 else '***'
            print(f"✅ {display_name:.<40} {masked}")
            configured_count += 1

    print(f"\nConfigured: {configured_count}/5")

    if all_valid:
        print("\n✅ All Twitter API credentials are configured!")
        return True
    else:
        print("\n❌ Some credentials are missing. Please configure them in .env")
        return False


def test_twitter_connection():
    """Test Twitter API connection"""
    print_header("Testing Twitter API Connection")

    try:
        import tweepy
    except ImportError:
        print("❌ tweepy not installed. Run: pip install tweepy")
        return False

    load_dotenv()

    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

    if not bearer_token or bearer_token.startswith('your_'):
        print("❌ Bearer token not configured")
        return False

    try:
        print("🔄 Connecting to Twitter API...")
        client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)

        # Test with a simple query
        print("🔍 Running test query...")
        response = client.search_recent_tweets(
            query='OSINT',
            max_results=10,
            tweet_fields=['created_at']
        )

        if response.data:
            print(f"✅ Connection successful!")
            print(f"   Found {len(response.data)} tweets in test query")
            print(f"   Sample: {response.data[0].text[:80]}...")
            return True
        else:
            print("⚠️  Connection successful but no results returned")
            return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        if "Unauthorized" in str(e):
            print("   • Check your Bearer Token is correct")
            print("   • Verify your Twitter Developer account is active")
        elif "rate_limit" in str(e).lower():
            print("   • You may have hit the rate limit")
            print("   • Wait a few minutes and try again")
        return False


def show_setup_guide():
    """Show step-by-step setup guide"""
    print_header("Twitter API Setup Guide")

    guide = """
STEP 1: Create Twitter Developer Account
   1. Go to https://developer.twitter.com/en/portal/dashboard
   2. Sign in with your Twitter account (create one if needed)
   3. Click "Create Project"
   4. Give it a name (e.g., "OSINT Monitor")
   5. Select "Research" as use case
   6. Describe: "Social media monitoring and OSINT research"
   7. Create the project

STEP 2: Create an App
   1. In your project, click "Create App"
   2. Name it (e.g., "osint-monitor")
   3. Keep the credentials safe!

STEP 3: Get Your API Keys
   1. Go to "Keys and tokens" tab
   2. Copy your API Key → TWITTER_API_KEY
   3. Copy API Key Secret → TWITTER_API_SECRET
   4. Generate Access Token → TWITTER_ACCESS_TOKEN
   5. Copy Access Token Secret → TWITTER_ACCESS_TOKEN_SECRET
   6. Find Bearer Token → TWITTER_BEARER_TOKEN

STEP 4: Configure .env
   1. Edit the .env file in your project directory
   2. Replace placeholder values with your actual credentials
   3. Save the file

STEP 5: Test Configuration
   1. Run: python setup_twitter_api.py
   2. Select "Validate Credentials"
   3. All should show ✅

STEP 6: Use OSINT Monitor
   1. python osint_monitor.py "nrk8286"
   2. Twitter searches will now work!

⚠️  SECURITY REMINDERS:
   • Never commit .env to GitHub
   • Keep your tokens secret
   • Regenerate if compromised
   • .env should be in .gitignore
"""
    print(guide)


def show_interactive_menu():
    """Show interactive menu"""
    print_header("Twitter API Setup Assistant")

    options = {
        '1': ('Show Setup Guide', show_setup_guide),
        '2': ('Create .env File', lambda: create_env_file()),
        '3': ('Validate Credentials', validate_credentials),
        '4': ('Test Connection', test_twitter_connection),
        '5': ('Full Setup Check', run_full_check),
        '6': ('Exit', lambda: sys.exit(0)),
    }

    while True:
        print("\nWhat would you like to do?")
        for key, (name, _) in options.items():
            print(f"  {key}. {name}")

        choice = input("\nSelect option (1-6): ").strip()

        if choice in options:
            name, func = options[choice]
            if choice != '6':
                func()
                input("\nPress Enter to continue...")
        else:
            print("❌ Invalid option")


def run_full_check():
    """Run complete setup check"""
    print_header("Full Setup Check")

    checks = [
        (".env file exists", check_env_file),
        ("Credentials configured", validate_credentials),
        ("Twitter API connection", test_twitter_connection),
    ]

    results = []
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))
        print()

    print_header("Setup Check Summary")

    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")

    all_passed = all(r for _, r in results)

    if all_passed:
        print("\n🎉 All checks passed! Ready to use OSINT Monitor with Twitter API")
        print("\nNext step: python osint_monitor.py \"keyword\"")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nRun again: python setup_twitter_api.py")


def main():
    """Main function"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║        Twitter API Configuration for OSINT Monitor         ║
    ║                                                            ║
    ║  This tool helps you set up and validate Twitter API      ║
    ║  credentials for use with the OSINT Monitor application.  ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    # If command line argument provided
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == '--validate':
            validate_credentials()
        elif command == '--test':
            test_twitter_connection()
        elif command == '--create-env':
            create_env_file()
        elif command == '--check':
            run_full_check()
        elif command in ['--help', '-h']:
            print("""
Usage: python setup_twitter_api.py [option]

Options:
  (no args)        Interactive menu
  --validate       Check credentials
  --test           Test API connection
  --create-env     Create .env file
  --check          Run full setup check
  --help           Show this help

Examples:
  python setup_twitter_api.py
  python setup_twitter_api.py --validate
  python setup_twitter_api.py --check
            """)
        else:
            print(f"Unknown option: {command}")
            print("Run with --help for usage information")
    else:
        # Show interactive menu
        show_interactive_menu()


if __name__ == "__main__":
    main()

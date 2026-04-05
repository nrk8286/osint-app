#!/usr/bin/env python3
"""
Recon-ng Integration Examples
Demonstrates various ways to use Recon-ng with OSINT Monitor
"""

from osint_monitor import OSINTMonitor
from recon_ng_wrapper import ReconNgWrapper
from datetime import datetime


def example_1_basic_domain_recon():
    """Example 1: Basic domain reconnaissance"""
    print("\n" + "="*60)
    print("Example 1: Basic Domain Reconnaissance")
    print("="*60 + "\n")

    monitor = OSINTMonitor()

    # Check if Recon-ng is available
    if not monitor.recon_ng or not monitor.recon_ng.is_available():
        print("Recon-ng not available. Install it first:")
        print("  git clone https://github.com/lanmaster53/recon-ng.git")
        print("  cd recon-ng && pip install -r requirements.txt")
        return

    # Perform domain reconnaissance
    domain = "example.com"
    results = monitor.recon_domain(domain)

    print(f"\nReconnaissance Results for {domain}:")
    for result in results:
        print(f"  Type: {result.get('type', 'unknown')}")
        print(f"  Module: {result.get('module', 'unknown')}")
        print(f"  Output: {result.get('output', '')[:200]}...")
        print()


def example_2_email_harvesting():
    """Example 2: Email harvesting from domain"""
    print("\n" + "="*60)
    print("Example 2: Email Harvesting")
    print("="*60 + "\n")

    monitor = OSINTMonitor()

    if not monitor.recon_ng or not monitor.recon_ng.is_available():
        print("Recon-ng not available")
        return

    domain = "example.com"
    emails = monitor.harvest_emails(domain)

    print(f"\nEmails harvested for {domain}:")
    if emails:
        for email in emails:
            print(f"  - {email.get('value', 'unknown')}")
            if email.get('module'):
                print(f"    (from {email['module']})")
    else:
        print("  No emails found")


def example_3_combined_osint():
    """Example 3: Combine multiple OSINT sources"""
    print("\n" + "="*60)
    print("Example 3: Combined OSINT Sources")
    print("="*60 + "\n")

    monitor = OSINTMonitor()

    domain = "example.com"

    # Use Recon-ng if available
    use_recon = monitor.recon_ng and monitor.recon_ng.is_available()

    # Collect mentions from all sources
    mentions = monitor.collect_mentions(
        keyword=domain,
        google_results=5,
        twitter_results=5,
        scrape_urls=[],  # Add URLs if desired
        use_recon_ng=use_recon
    )

    # Save results
    monitor.save_to_csv()

    print(f"\nTotal sources utilized:")
    sources = set(m.get('source', 'unknown') for m in mentions)
    for source in sorted(sources):
        count = sum(1 for m in mentions if m.get('source') == source)
        print(f"  - {source}: {count} results")


def example_4_batch_domain_processing():
    """Example 4: Process multiple domains in batch"""
    print("\n" + "="*60)
    print("Example 4: Batch Domain Processing")
    print("="*60 + "\n")

    monitor = OSINTMonitor()

    if not monitor.recon_ng or not monitor.recon_ng.is_available():
        print("Recon-ng not available")
        return

    domains = ["example.com", "google.com", "github.com"]

    print(f"Processing {len(domains)} domains...\n")

    for domain in domains:
        print(f"Analyzing {domain}...")
        results = monitor.recon_domain(domain)
        print(f"  Found {len(results)} results")

    # Save all results
    if monitor.mentions:
        monitor.save_to_csv()
        print(f"\nSaved {len(monitor.mentions)} total results to CSV")


def example_5_direct_wrapper_usage():
    """Example 5: Direct usage of ReconNgWrapper"""
    print("\n" + "="*60)
    print("Example 5: Direct ReconNgWrapper Usage")
    print("="*60 + "\n")

    recon = ReconNgWrapper()

    if not recon.is_available():
        print("Recon-ng not available")
        return

    # Check available modules
    print("Available Recon-ng modules:")
    modules = recon.get_available_modules()
    if modules:
        for module in modules[:10]:  # Show first 10
            print(f"  - {module}")
        if len(modules) > 10:
            print(f"  ... and {len(modules) - 10} more modules")
    else:
        print("  Could not retrieve modules list")

    # Run domain enumeration
    print("\nPerforming domain enumeration...")
    results = recon.enumerate_domain("example.com")

    for result in results:
        print(f"  {result.get('type', 'unknown')}: {result.get('module', 'unknown')}")


def example_6_custom_workspace():
    """Example 6: Working with custom workspaces"""
    print("\n" + "="*60)
    print("Example 6: Custom Workspace Management")
    print("="*60 + "\n")

    recon = ReconNgWrapper()

    if not recon.is_available():
        print("Recon-ng not available")
        return

    workspace_name = f"custom_workspace_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print(f"Creating workspace: {workspace_name}")
    if recon.create_workspace(workspace_name):
        print(f"✓ Workspace created successfully")

        # Try to run a module in the workspace
        print(f"Running module in workspace...")
        result = recon.run_module(
            workspace_name,
            "recon/domains-hosts/dns_subdomain_enum",
            {"SOURCE": "example.com"}
        )

        if result and result['success']:
            print(f"✓ Module executed successfully")
            print(f"  Output preview: {result['output'][:100]}...")
        else:
            print(f"✗ Module execution failed: {result.get('error', 'unknown error')}")

        # Clean up
        print(f"Deleting workspace...")
        if recon._delete_workspace(workspace_name):
            print(f"✓ Workspace deleted")
    else:
        print(f"✗ Failed to create workspace")


def main():
    """Run all examples"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║      Recon-ng Integration Examples for OSINT Monitor       ║
    ║                                                            ║
    ║  These examples show how to use Recon-ng with the         ║
    ║  OSINT Monitor application for advanced reconnaissance.    ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    examples = [
        ("Basic Domain Recon", example_1_basic_domain_recon),
        ("Email Harvesting", example_2_email_harvesting),
        ("Combined OSINT", example_3_combined_osint),
        ("Batch Processing", example_4_batch_domain_processing),
        ("Direct Wrapper Usage", example_5_direct_wrapper_usage),
        ("Custom Workspace", example_6_custom_workspace),
    ]

    while True:
        print("\nAvailable Examples:")
        for i, (name, _) in enumerate(examples, 1):
            print(f"  {i}. {name}")
        print(f"  0. Exit")

        choice = input("\nSelect an example to run (0-{0}): ".format(len(examples))).strip()

        if choice == "0":
            print("Exiting...")
            break

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(examples):
                name, func = examples[idx]
                print(f"\nRunning: {name}")
                func()
            else:
                print("Invalid selection")
        except ValueError:
            print("Please enter a valid number")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()

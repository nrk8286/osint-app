#!/usr/bin/env python3
"""
Recon-ng Wrapper Module
Integrates recon-ng reconnaissance framework with OSINT Monitor.

Recon-ng is a powerful framework for OSINT reconnaissance tasks including:
- Domain enumeration and reconnaissance
- Email harvesting
- Phone number discovery
- Social media profiling
- And much more
"""

import os
import subprocess
import json
from typing import List, Dict, Optional
from datetime import datetime
import tempfile
import shutil


class ReconNgWrapper:
    """Wrapper for recon-ng framework to integrate with OSINT Monitor."""

    def __init__(self):
        """Initialize recon-ng wrapper."""
        self.recon_ng_available = self._check_recon_ng()
        self.workspace = None

    def _check_recon_ng(self) -> bool:
        """Check if recon-ng is available on the system."""
        try:
            result = subprocess.run(
                ['recon-ng', '-v'],
                capture_output=True,
                timeout=5,
                text=True
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def is_available(self) -> bool:
        """Check if recon-ng is available."""
        return self.recon_ng_available

    def create_workspace(self, name: str) -> bool:
        """
        Create a recon-ng workspace.

        Args:
            name: Workspace name

        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ['recon-ng', '-w', name, '--no-prompt'],
                capture_output=True,
                timeout=10,
                text=True
            )
            if result.returncode == 0:
                self.workspace = name
                return True
            return False
        except Exception as e:
            print(f"Error creating workspace: {e}")
            return False

    def run_module(self, workspace: str, module: str, options: Dict[str, str]) -> Optional[Dict]:
        """
        Run a recon-ng module within a workspace.

        Args:
            workspace: Workspace name
            module: Module path (e.g., 'recon/domains-companies/whois_netblocks')
            options: Dictionary of options to set {key: value}

        Returns:
            Dictionary with results or None if failed
        """
        try:
            # Build recon-ng command with options
            cmd = ['recon-ng', '-w', workspace]

            # Build the command string for recon-ng shell
            commands = []

            # Set all options
            for key, value in options.items():
                commands.append(f"set {key} {value}")

            # Load and run the module
            commands.append(f"use {module}")
            commands.append("run")

            command_str = '\n'.join(commands)

            # Run recon-ng with commands
            result = subprocess.run(
                cmd,
                input=command_str,
                capture_output=True,
                timeout=30,
                text=True
            )

            if result.returncode == 0:
                return {
                    'success': True,
                    'output': result.stdout,
                    'module': module
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr,
                    'module': module
                }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Module execution timeout',
                'module': module
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'module': module
            }

    def harvest_emails(self, domain: str, workspace: str = None) -> List[Dict]:
        """
        Harvest emails for a domain using recon-ng email modules.

        Args:
            domain: Domain to harvest emails from
            workspace: Workspace name (auto-generated if None)

        Returns:
            List of harvested email dictionaries
        """
        if not self.recon_ng_available:
            print("Recon-ng is not available. Install it: https://github.com/lanmaster53/recon-ng")
            return []

        emails = []
        workspace = workspace or f"osint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        try:
            # Create workspace
            if not self.create_workspace(workspace):
                print(f"Failed to create workspace: {workspace}")
                return []

            print(f"Harvesting emails for domain: {domain}")

            # List of email harvesting modules to try
            email_modules = [
                'recon/domains-companies/whois_companies',
                'recon/companies-contacts/linkedin_linkedin',
                'recon/domains-hosts/dns_subdomain_enum',
            ]

            for module in email_modules:
                try:
                    result = self.run_module(
                        workspace,
                        module,
                        {'SOURCE': domain}
                    )

                    if result and result['success']:
                        print(f"  Module '{module}' executed successfully")
                        # Parse output for emails (simplified)
                        output_lines = result['output'].split('\n')
                        for line in output_lines:
                            if '@' in line:
                                emails.append({
                                    'source': 'Recon-ng',
                                    'type': 'email',
                                    'value': line.strip(),
                                    'module': module,
                                    'domain': domain,
                                    'timestamp': datetime.now().isoformat()
                                })
                except Exception as e:
                    print(f"  Error running module {module}: {e}")

            # Clean up workspace
            self._delete_workspace(workspace)

            return emails

        except Exception as e:
            print(f"Error during email harvesting: {e}")
            return []

    def enumerate_domain(self, domain: str, workspace: str = None) -> List[Dict]:
        """
        Perform comprehensive domain enumeration using recon-ng.

        Args:
            domain: Domain to enumerate
            workspace: Workspace name (auto-generated if None)

        Returns:
            List of enumeration results
        """
        if not self.recon_ng_available:
            print("Recon-ng is not available")
            return []

        results = []
        workspace = workspace or f"osint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        try:
            if not self.create_workspace(workspace):
                return []

            print(f"Enumerating domain: {domain}")

            # Domain enumeration modules
            enum_modules = [
                ('recon/domains-hosts/dns_subdomain_enum', 'subdomain'),
                ('recon/domains-hosts/ssl_certificate_enum', 'certificate'),
                ('recon/domains-companies/whois_companies', 'whois'),
            ]

            for module, result_type in enum_modules:
                try:
                    result = self.run_module(
                        workspace,
                        module,
                        {'SOURCE': domain}
                    )

                    if result and result['success']:
                        print(f"  {result_type.capitalize()} enumeration completed")
                        results.append({
                            'source': 'Recon-ng',
                            'type': result_type,
                            'domain': domain,
                            'module': module,
                            'output': result['output'][:500],  # First 500 chars
                            'timestamp': datetime.now().isoformat()
                        })
                except Exception as e:
                    print(f"  Error with {result_type} enumeration: {e}")

            # Clean up
            self._delete_workspace(workspace)

            return results

        except Exception as e:
            print(f"Error during domain enumeration: {e}")
            return []

    def _delete_workspace(self, workspace: str) -> bool:
        """
        Delete a workspace.

        Args:
            workspace: Workspace name

        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ['recon-ng', '-w', workspace, '--delete', '--no-prompt'],
                capture_output=True,
                timeout=10,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_available_modules(self) -> List[str]:
        """
        Get list of available recon-ng modules.

        Returns:
            List of module names
        """
        try:
            result = subprocess.run(
                ['recon-ng', '--modules'],
                capture_output=True,
                timeout=10,
                text=True
            )

            if result.returncode == 0:
                modules = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                return modules
            return []
        except Exception:
            return []

#!/usr/bin/env python3
"""
Setup script for OSINT Monitor
Enables pip installation of the OSINT monitoring application
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="osint-monitor",
    version="1.0.0",
    author="nrk8286",
    author_email="nrk8286@gmail.com",
    description="Advanced OSINT Social Media Monitoring and Intelligence Gathering Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nrk8286/osint-app",
    project_urls={
        "Bug Tracker": "https://github.com/nrk8286/osint-app/issues",
        "Documentation": "https://github.com/nrk8286/osint-app#readme",
        "Source Code": "https://github.com/nrk8286/osint-app",
    },
    packages=find_packages(exclude=["tests"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.7",
    install_requires=[
        "googlesearch-python>=1.2.3",
        "tweepy>=4.14.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "pandas>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "recon-ng": [
            "# Recon-ng should be installed separately",
            "# See RECON_NG_SETUP.md for instructions",
        ],
    },
    # Note: Entry points refer to functions, but these are script files
    # Users can run: python osint_monitor.py or python setup_twitter_api.py
    keywords=[
        "osint",
        "social-media",
        "monitoring",
        "intelligence",
        "reconnaissance",
        "security",
        "research",
        "twitter",
        "google",
        "web-scraping",
    ],
    zip_safe=False,
)

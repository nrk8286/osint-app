"""Setup script for OSINT Monitoring Platform."""

"""
Setup configuration for OSINT App.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="osint-monitoring-platform",
    version="2.0.0",
    author="OSINT Team",
    description="Production-ready OSINT monitoring and data collection platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nrk8286/osint-app",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    name="osint-app",
    version="0.1.0",
    author="OSINT App Team",
    description="A simple OSINT application for monitoring social media mentions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nrk8286/osint-app",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "osint-monitor=osint_app.cli:main",
            "osint-api=osint_app.api.main:main",
        ],
    },
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "osint-app=osint_app.cli:cli",
        ],
    },
)

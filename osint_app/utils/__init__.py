"""Utility functions for OSINT app."""

from textblob import TextBlob
from typing import Optional
import re


def analyze_sentiment(text: str) -> str:
    """
    Analyze sentiment of text using TextBlob.
    
    Args:
        text: Text to analyze
        
    Returns:
        Sentiment classification: 'positive', 'negative', or 'neutral'
    """
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            return 'positive'
        elif polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'
    except Exception as e:
        return 'neutral'


def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    # Remove URLs
    text = re.sub(r'http\S+|www.\S+', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text.strip()


def extract_hashtags(text: str) -> list:
    """
    Extract hashtags from text.
    
    Args:
        text: Text to extract hashtags from
        
    Returns:
        List of hashtags
    """
    hashtags = re.findall(r'#\w+', text)
    return hashtags


def extract_mentions(text: str) -> list:
    """
    Extract @mentions from text.
    
    Args:
        text: Text to extract mentions from
        
    Returns:
        List of mentions
    """
    mentions = re.findall(r'@\w+', text)
    return mentions


def format_engagement(likes: int = 0, shares: int = 0, comments: int = 0) -> dict:
    """
    Format engagement metrics.
    
    Args:
        likes: Number of likes
        shares: Number of shares
        comments: Number of comments
        
    Returns:
        Dictionary of engagement metrics
    """
    return {
        'likes': likes,
        'shares': shares,
        'comments': comments,
        'total': likes + shares + comments
    }

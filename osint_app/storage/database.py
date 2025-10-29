"""
Database storage for OSINT data.
"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from tinydb import TinyDB, Query


class Database:
    """Database manager for OSINT mentions."""
    
    def __init__(self, db_path: str = "./data/osint.db"):
        """
        Initialize the database.
        
        Args:
            db_path: Path to the database file
        """
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.db = TinyDB(db_path)
        self.mentions = self.db.table('mentions')
        self.queries = self.db.table('queries')
    
    def save_mention(self, mention: Dict[str, Any]) -> int:
        """
        Save a single mention to the database.
        
        Args:
            mention: Mention dictionary
            
        Returns:
            Document ID of the saved mention
        """
        mention['saved_at'] = datetime.now().isoformat()
        return self.mentions.insert(mention)
    
    def save_mentions(self, mentions: List[Dict[str, Any]]) -> List[int]:
        """
        Save multiple mentions to the database.
        
        Args:
            mentions: List of mention dictionaries
            
        Returns:
            List of document IDs
        """
        for mention in mentions:
            mention['saved_at'] = datetime.now().isoformat()
        return self.mentions.insert_multiple(mentions)
    
    def get_mentions(self, limit: Optional[int] = None, 
                     source: Optional[str] = None,
                     keyword: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve mentions from the database.
        
        Args:
            limit: Maximum number of mentions to retrieve
            source: Filter by source platform
            keyword: Filter by keyword
            
        Returns:
            List of mentions
        """
        Mention = Query()
        
        if source and keyword:
            results = self.mentions.search(
                (Mention.source == source) & (Mention.keywords.any([keyword]))
            )
        elif source:
            results = self.mentions.search(Mention.source == source)
        elif keyword:
            results = self.mentions.search(Mention.keywords.any([keyword]))
        else:
            results = self.mentions.all()
        
        if limit:
            return results[:limit]
        return results
    
    def get_by_sentiment(self, sentiment: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get mentions by sentiment.
        
        Args:
            sentiment: Sentiment type (positive, negative, neutral)
            limit: Maximum number of results
            
        Returns:
            List of mentions with specified sentiment
        """
        Mention = Query()
        results = self.mentions.search(Mention.sentiment.sentiment == sentiment)
        
        if limit:
            return results[:limit]
        return results
    
    def save_query(self, keywords: List[str], sources: List[str], 
                   results_count: int) -> int:
        """
        Save a query record.
        
        Args:
            keywords: Keywords used in the query
            sources: Sources queried
            results_count: Number of results found
            
        Returns:
            Document ID of the saved query
        """
        query_record = {
            'keywords': keywords,
            'sources': sources,
            'results_count': results_count,
            'timestamp': datetime.now().isoformat()
        }
        return self.queries.insert(query_record)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with database statistics
        """
        all_mentions = self.mentions.all()
        
        sources = {}
        sentiments = {"positive": 0, "negative": 0, "neutral": 0}
        
        for mention in all_mentions:
            source = mention.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
            
            sentiment_data = mention.get('sentiment', {})
            sentiment = sentiment_data.get('sentiment', 'neutral')
            if sentiment in sentiments:
                sentiments[sentiment] += 1
        
        return {
            'total_mentions': len(all_mentions),
            'sources': sources,
            'sentiments': sentiments,
            'total_queries': len(self.queries.all())
        }
    
    def clear_mentions(self):
        """Clear all mentions from the database."""
        self.mentions.truncate()
    
    def clear_all(self):
        """Clear all data from the database."""
        self.mentions.truncate()
        self.queries.truncate()
    
    def close(self):
        """Close the database connection."""
        self.db.close()

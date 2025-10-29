"""
Sentiment analyzer for OSINT mentions.
"""
from textblob import TextBlob
from typing import Dict, Any, List


class SentimentAnalyzer:
    """Analyze sentiment of collected mentions."""
    
    def __init__(self):
        """Initialize the sentiment analyzer."""
        pass
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Classify sentiment
        if polarity > 0.1:
            sentiment = "positive"
        elif polarity < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "polarity": polarity,
            "subjectivity": subjectivity,
            "score": self._calculate_score(polarity, subjectivity)
        }
    
    def _calculate_score(self, polarity: float, subjectivity: float) -> float:
        """
        Calculate overall sentiment score.
        
        Args:
            polarity: Sentiment polarity (-1 to 1)
            subjectivity: Sentiment subjectivity (0 to 1)
            
        Returns:
            Overall sentiment score
        """
        # Weight polarity more heavily than subjectivity
        return (polarity * 0.7 + (1 - subjectivity) * 0.3)
    
    def analyze_batch(self, mentions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze sentiment for multiple mentions.
        
        Args:
            mentions: List of mention dictionaries
            
        Returns:
            List of mentions with sentiment analysis added
        """
        for mention in mentions:
            if "text" in mention:
                sentiment_result = self.analyze(mention["text"])
                mention["sentiment"] = sentiment_result
        
        return mentions
    
    def get_statistics(self, mentions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get sentiment statistics for mentions.
        
        Args:
            mentions: List of analyzed mentions
            
        Returns:
            Dictionary with sentiment statistics
        """
        if not mentions:
            return {
                "total": 0,
                "positive": 0,
                "negative": 0,
                "neutral": 0,
                "avg_polarity": 0.0,
                "avg_subjectivity": 0.0
            }
        
        sentiments = [m.get("sentiment", {}) for m in mentions if "sentiment" in m]
        
        positive = sum(1 for s in sentiments if s.get("sentiment") == "positive")
        negative = sum(1 for s in sentiments if s.get("sentiment") == "negative")
        neutral = sum(1 for s in sentiments if s.get("sentiment") == "neutral")
        
        polarities = [s.get("polarity", 0) for s in sentiments]
        subjectivities = [s.get("subjectivity", 0) for s in sentiments]
        
        return {
            "total": len(mentions),
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "avg_polarity": sum(polarities) / len(polarities) if polarities else 0.0,
            "avg_subjectivity": sum(subjectivities) / len(subjectivities) if subjectivities else 0.0,
            "positive_pct": (positive / len(mentions) * 100) if mentions else 0.0,
            "negative_pct": (negative / len(mentions) * 100) if mentions else 0.0,
            "neutral_pct": (neutral / len(mentions) * 100) if mentions else 0.0
        }

"""
Unit tests for OSINT App sentiment analyzer.
"""
import unittest
from osint_app.analyzers.sentiment import SentimentAnalyzer


class TestSentimentAnalyzer(unittest.TestCase):
    """Test sentiment analyzer functionality."""
    
    def setUp(self):
        """Set up test fixture."""
        self.analyzer = SentimentAnalyzer()
    
    def test_analyze_positive(self):
        """Test positive sentiment analysis."""
        result = self.analyzer.analyze("I love this amazing product!")
        
        self.assertIn("sentiment", result)
        self.assertIn("polarity", result)
        self.assertIn("subjectivity", result)
        self.assertEqual(result["sentiment"], "positive")
        self.assertGreater(result["polarity"], 0)
    
    def test_analyze_negative(self):
        """Test negative sentiment analysis."""
        result = self.analyzer.analyze("This is terrible and awful.")
        
        self.assertEqual(result["sentiment"], "negative")
        self.assertLess(result["polarity"], 0)
    
    def test_analyze_neutral(self):
        """Test neutral sentiment analysis."""
        result = self.analyzer.analyze("The sky is blue.")
        
        self.assertEqual(result["sentiment"], "neutral")
        self.assertAlmostEqual(result["polarity"], 0, delta=0.2)
    
    def test_analyze_batch(self):
        """Test batch sentiment analysis."""
        mentions = [
            {"text": "Great product!"},
            {"text": "Terrible experience."},
            {"text": "It exists."}
        ]
        
        results = self.analyzer.analyze_batch(mentions)
        
        self.assertEqual(len(results), 3)
        for mention in results:
            self.assertIn("sentiment", mention)
    
    def test_get_statistics(self):
        """Test sentiment statistics."""
        mentions = [
            {"text": "Great!", "sentiment": {"sentiment": "positive", "polarity": 0.5, "subjectivity": 0.6}},
            {"text": "Awful!", "sentiment": {"sentiment": "negative", "polarity": -0.5, "subjectivity": 0.6}},
            {"text": "Okay.", "sentiment": {"sentiment": "neutral", "polarity": 0.0, "subjectivity": 0.2}}
        ]
        
        stats = self.analyzer.get_statistics(mentions)
        
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["positive"], 1)
        self.assertEqual(stats["negative"], 1)
        self.assertEqual(stats["neutral"], 1)
        self.assertAlmostEqual(stats["avg_polarity"], 0.0, delta=0.1)
    
    def test_get_statistics_empty(self):
        """Test statistics with empty mentions."""
        stats = self.analyzer.get_statistics([])
        
        self.assertEqual(stats["total"], 0)
        self.assertEqual(stats["positive"], 0)
        self.assertEqual(stats["negative"], 0)
        self.assertEqual(stats["neutral"], 0)


if __name__ == '__main__':
    unittest.main()

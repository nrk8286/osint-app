"""
Unit tests for OSINT App collectors.
"""
import unittest
from osint_app.collectors.base import BaseCollector
from osint_app.collectors.web_collector import (
    WebSearchCollector, NewsCollector, SocialMediaCollector
)


class TestBaseCollector(unittest.TestCase):
    """Test base collector functionality."""
    
    def test_create_mention(self):
        """Test creating a standardized mention."""
        # Create a simple concrete implementation for testing
        class TestCollector(BaseCollector):
            def collect(self):
                return []
        
        collector = TestCollector(keywords=["test"])
        mention = collector._create_mention(
            text="This is a test mention",
            source="test_source",
            url="https://example.com",
            author="test_author"
        )
        
        self.assertEqual(mention["text"], "This is a test mention")
        self.assertEqual(mention["source"], "test_source")
        self.assertEqual(mention["url"], "https://example.com")
        self.assertEqual(mention["author"], "test_author")
        self.assertIn("timestamp", mention)
        self.assertIn("keywords", mention)
    
    def test_extract_keywords(self):
        """Test keyword extraction from text."""
        class TestCollector(BaseCollector):
            def collect(self):
                return []
        
        collector = TestCollector(keywords=["Python", "AI", "Machine Learning"])
        
        # Test with matching keywords
        keywords = collector._extract_keywords("I love Python and AI")
        self.assertIn("Python", keywords)
        self.assertIn("AI", keywords)
        
        # Test case insensitivity
        keywords = collector._extract_keywords("python is great")
        self.assertIn("Python", keywords)
        
        # Test with no matches
        keywords = collector._extract_keywords("Nothing to see here")
        self.assertEqual(len(keywords), 0)


class TestWebSearchCollector(unittest.TestCase):
    """Test web search collector."""
    
    def test_initialization(self):
        """Test collector initialization."""
        keywords = ["Python", "AI"]
        collector = WebSearchCollector(keywords, max_results=5)
        
        self.assertEqual(collector.keywords, keywords)
        self.assertEqual(collector.max_results, 5)
    
    def test_collect(self):
        """Test collecting mentions."""
        collector = WebSearchCollector(["Python"], max_results=10)
        results = collector.collect()
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Check first result structure
        first = results[0]
        self.assertIn("text", first)
        self.assertIn("source", first)
        self.assertEqual(first["source"], "web_search")


class TestNewsCollector(unittest.TestCase):
    """Test news collector."""
    
    def test_initialization(self):
        """Test collector initialization."""
        keywords = ["Technology"]
        collector = NewsCollector(keywords, max_results=10)
        
        self.assertEqual(collector.keywords, keywords)
        self.assertEqual(collector.max_results, 10)
    
    def test_collect(self):
        """Test collecting news."""
        collector = NewsCollector(["AI"], max_results=5)
        results = collector.collect()
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Check result structure
        first = results[0]
        self.assertEqual(first["source"], "news")


class TestSocialMediaCollector(unittest.TestCase):
    """Test social media collector."""
    
    def test_initialization(self):
        """Test collector initialization."""
        keywords = ["Test"]
        platforms = ["twitter", "reddit"]
        collector = SocialMediaCollector(keywords, platforms)
        
        self.assertEqual(collector.keywords, keywords)
        self.assertEqual(collector.platforms, platforms)
    
    def test_collect(self):
        """Test collecting from social media."""
        collector = SocialMediaCollector(["Python"], ["twitter"])
        results = collector.collect()
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Check result structure
        first = results[0]
        self.assertEqual(first["source"], "twitter")


if __name__ == '__main__':
    unittest.main()

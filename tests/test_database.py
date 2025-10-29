"""
Unit tests for OSINT App database storage.
"""
import unittest
import os
import tempfile
from osint_app.storage.database import Database


class TestDatabase(unittest.TestCase):
    """Test database functionality."""
    
    def setUp(self):
        """Set up test fixture with temporary database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_osint.db")
        self.db = Database(self.db_path)
    
    def tearDown(self):
        """Clean up test database."""
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)
    
    def test_save_mention(self):
        """Test saving a single mention."""
        mention = {
            "text": "Test mention",
            "source": "test",
            "keywords": ["test"]
        }
        
        doc_id = self.db.save_mention(mention)
        self.assertIsInstance(doc_id, int)
        
        # Verify it was saved
        mentions = self.db.get_mentions()
        self.assertEqual(len(mentions), 1)
        self.assertEqual(mentions[0]["text"], "Test mention")
    
    def test_save_mentions(self):
        """Test saving multiple mentions."""
        mentions = [
            {"text": "Mention 1", "source": "test", "keywords": ["test"]},
            {"text": "Mention 2", "source": "test", "keywords": ["test"]},
        ]
        
        doc_ids = self.db.save_mentions(mentions)
        self.assertEqual(len(doc_ids), 2)
        
        # Verify they were saved
        saved_mentions = self.db.get_mentions()
        self.assertEqual(len(saved_mentions), 2)
    
    def test_get_mentions_with_filter(self):
        """Test retrieving mentions with filters."""
        mentions = [
            {"text": "Twitter mention", "source": "twitter", "keywords": ["Python"]},
            {"text": "Reddit mention", "source": "reddit", "keywords": ["AI"]},
        ]
        self.db.save_mentions(mentions)
        
        # Filter by source
        twitter_mentions = self.db.get_mentions(source="twitter")
        self.assertEqual(len(twitter_mentions), 1)
        self.assertEqual(twitter_mentions[0]["source"], "twitter")
        
        # Filter by keyword
        python_mentions = self.db.get_mentions(keyword="Python")
        self.assertEqual(len(python_mentions), 1)
    
    def test_get_mentions_with_limit(self):
        """Test retrieving mentions with limit."""
        mentions = [
            {"text": f"Mention {i}", "source": "test", "keywords": ["test"]}
            for i in range(10)
        ]
        self.db.save_mentions(mentions)
        
        limited = self.db.get_mentions(limit=5)
        self.assertEqual(len(limited), 5)
    
    def test_get_by_sentiment(self):
        """Test retrieving mentions by sentiment."""
        mentions = [
            {
                "text": "Positive mention",
                "source": "test",
                "keywords": ["test"],
                "sentiment": {"sentiment": "positive"}
            },
            {
                "text": "Negative mention",
                "source": "test",
                "keywords": ["test"],
                "sentiment": {"sentiment": "negative"}
            },
        ]
        self.db.save_mentions(mentions)
        
        positive = self.db.get_by_sentiment("positive")
        self.assertEqual(len(positive), 1)
        self.assertEqual(positive[0]["text"], "Positive mention")
    
    def test_save_query(self):
        """Test saving query records."""
        doc_id = self.db.save_query(
            keywords=["test"],
            sources=["web"],
            results_count=5
        )
        
        self.assertIsInstance(doc_id, int)
    
    def test_get_statistics(self):
        """Test database statistics."""
        mentions = [
            {
                "text": "Tweet",
                "source": "twitter",
                "keywords": ["test"],
                "sentiment": {"sentiment": "positive"}
            },
            {
                "text": "Post",
                "source": "reddit",
                "keywords": ["test"],
                "sentiment": {"sentiment": "negative"}
            },
        ]
        self.db.save_mentions(mentions)
        self.db.save_query(["test"], ["social"], 2)
        
        stats = self.db.get_statistics()
        
        self.assertEqual(stats["total_mentions"], 2)
        self.assertEqual(stats["sources"]["twitter"], 1)
        self.assertEqual(stats["sources"]["reddit"], 1)
        self.assertEqual(stats["sentiments"]["positive"], 1)
        self.assertEqual(stats["sentiments"]["negative"], 1)
        self.assertEqual(stats["total_queries"], 1)
    
    def test_clear_mentions(self):
        """Test clearing mentions."""
        mentions = [
            {"text": "Mention 1", "source": "test", "keywords": ["test"]},
        ]
        self.db.save_mentions(mentions)
        
        self.db.clear_mentions()
        
        all_mentions = self.db.get_mentions()
        self.assertEqual(len(all_mentions), 0)
    
    def test_clear_all(self):
        """Test clearing all data."""
        mentions = [{"text": "Test", "source": "test", "keywords": ["test"]}]
        self.db.save_mentions(mentions)
        self.db.save_query(["test"], ["web"], 1)
        
        self.db.clear_all()
        
        stats = self.db.get_statistics()
        self.assertEqual(stats["total_mentions"], 0)
        self.assertEqual(stats["total_queries"], 0)


if __name__ == '__main__':
    unittest.main()

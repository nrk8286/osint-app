"""Unit tests for the TextBlob-based SentimentAnalyzer in osint_app/analyzers/."""

import pytest

from osint_app.analyzers.sentiment import SentimentAnalyzer


@pytest.fixture
def analyzer():
    return SentimentAnalyzer()


class TestAnalyze:
    """Tests for SentimentAnalyzer.analyze."""

    def test_positive_text(self, analyzer):
        result = analyzer.analyze("This is a wonderful and amazing experience!")
        assert result["sentiment"] == "positive"
        assert result["polarity"] > 0.1

    def test_negative_text(self, analyzer):
        result = analyzer.analyze("This is terrible and awful. I hate it.")
        assert result["sentiment"] == "negative"
        assert result["polarity"] < -0.1

    def test_neutral_text(self, analyzer):
        result = analyzer.analyze("The document was submitted on Monday.")
        assert result["sentiment"] == "neutral"

    def test_result_contains_all_keys(self, analyzer):
        result = analyzer.analyze("some text")
        assert "sentiment" in result
        assert "polarity" in result
        assert "subjectivity" in result
        assert "score" in result

    def test_polarity_in_valid_range(self, analyzer):
        result = analyzer.analyze("A fairly good day overall")
        assert -1.0 <= result["polarity"] <= 1.0

    def test_subjectivity_in_valid_range(self, analyzer):
        result = analyzer.analyze("I think this is good")
        assert 0.0 <= result["subjectivity"] <= 1.0


class TestCalculateScore:
    """Tests for SentimentAnalyzer._calculate_score."""

    def test_positive_polarity_gives_positive_score(self, analyzer):
        score = analyzer._calculate_score(polarity=1.0, subjectivity=0.0)
        # polarity*0.7 + (1 - subjectivity)*0.3 = 0.7 + 0.3 = 1.0
        assert abs(score - 1.0) < 1e-9

    def test_negative_polarity_gives_negative_score(self, analyzer):
        score = analyzer._calculate_score(polarity=-1.0, subjectivity=0.5)
        assert score < 0

    def test_zero_polarity_reflects_objectivity(self, analyzer):
        score = analyzer._calculate_score(polarity=0.0, subjectivity=0.0)
        # 0.0*0.7 + 1.0*0.3 = 0.3
        assert abs(score - 0.3) < 1e-9


class TestAnalyzeBatch:
    """Tests for SentimentAnalyzer.analyze_batch."""

    def test_adds_sentiment_to_each_mention(self, analyzer):
        mentions = [
            {"text": "This is great!"},
            {"text": "This is terrible."},
        ]
        result = analyzer.analyze_batch(mentions)
        for mention in result:
            assert "sentiment" in mention
            assert "sentiment" in mention["sentiment"]

    def test_skips_mentions_without_text(self, analyzer):
        mentions = [{"source": "web"}, {"text": "Nice product"}]
        result = analyzer.analyze_batch(mentions)
        assert "sentiment" not in result[0]
        assert "sentiment" in result[1]

    def test_returns_same_list(self, analyzer):
        mentions = [{"text": "hello world"}]
        result = analyzer.analyze_batch(mentions)
        assert result is mentions

    def test_empty_list_returns_empty(self, analyzer):
        result = analyzer.analyze_batch([])
        assert result == []


class TestGetStatistics:
    """Tests for SentimentAnalyzer.get_statistics."""

    def test_empty_mentions_returns_zeroes(self, analyzer):
        stats = analyzer.get_statistics([])
        assert stats["total"] == 0
        assert stats["positive"] == 0
        assert stats["negative"] == 0
        assert stats["neutral"] == 0

    def test_counts_sentiments_correctly(self, analyzer):
        mentions = [
            {"text": "I love this!", "sentiment": {"sentiment": "positive", "polarity": 0.9, "subjectivity": 0.5}},
            {"text": "I hate this!", "sentiment": {"sentiment": "negative", "polarity": -0.8, "subjectivity": 0.6}},
            {"text": "It is what it is.", "sentiment": {"sentiment": "neutral", "polarity": 0.0, "subjectivity": 0.1}},
        ]
        stats = analyzer.get_statistics(mentions)
        assert stats["total"] == 3
        assert stats["positive"] == 1
        assert stats["negative"] == 1
        assert stats["neutral"] == 1

    def test_percentage_keys_present(self, analyzer):
        mentions = [
            {"text": "great", "sentiment": {"sentiment": "positive", "polarity": 0.8, "subjectivity": 0.5}}
        ]
        stats = analyzer.get_statistics(mentions)
        assert "positive_pct" in stats
        assert "negative_pct" in stats
        assert "neutral_pct" in stats

    def test_average_polarity_computed(self, analyzer):
        mentions = [
            {"text": "a", "sentiment": {"sentiment": "positive", "polarity": 0.4, "subjectivity": 0.5}},
            {"text": "b", "sentiment": {"sentiment": "positive", "polarity": 0.6, "subjectivity": 0.5}},
        ]
        stats = analyzer.get_statistics(mentions)
        assert abs(stats["avg_polarity"] - 0.5) < 1e-9

    def test_mentions_without_sentiment_counted_in_total_only(self, analyzer):
        mentions = [
            {"text": "no sentiment here"},  # no 'sentiment' key
            {"text": "good", "sentiment": {"sentiment": "positive", "polarity": 0.7, "subjectivity": 0.5}},
        ]
        stats = analyzer.get_statistics(mentions)
        assert stats["total"] == 2
        assert stats["positive"] == 1

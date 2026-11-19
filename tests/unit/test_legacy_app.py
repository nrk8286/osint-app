"""The original CLI must remain usable without changing the v2 collector schema."""

import json

import pytest

from osint_app.app import OSINTApp
from osint_app.models.schemas import Mention as CollectorMention
from osint_app.models.schemas import SourceType
from osint_app.monitors.helpers import analyze_sentiment


@pytest.mark.parametrize("platform", ["twitter", "reddit", "web"])
def test_demo_monitor_search_and_export(platform):
    app = OSINTApp()
    mentions = app.search(["example"], platforms=[platform], max_results=2)

    assert len(mentions) == 2
    assert all(mention.platform.lower() == platform for mention in mentions)
    assert app.get_platform_summary() == {mentions[0].platform: 2}
    assert app.filter_by_platform(platform) == mentions
    assert app.get_engagement_summary()["total"] == sum(
        mention.engagement["total"] for mention in mentions
    )
    exported = json.loads(json.dumps(app.export_results()))
    assert exported[0]["content"] == mentions[0].content
    assert exported[0]["timestamp"] == mentions[0].timestamp.isoformat()


def test_empty_explicit_results_do_not_fall_back_to_stored_mentions():
    app = OSINTApp()
    app.search(["example"], platforms=["web"], max_results=1)
    assert app.export_results([]) == []
    assert app.get_platform_summary([]) == {}
    assert app.get_engagement_summary([])["total"] == 0


def test_legacy_sentiment_uses_local_analyzer():
    assert analyze_sentiment("great excellent") == "positive"
    assert analyze_sentiment("") is None


def test_v2_collector_retains_numeric_engagement():
    mention = CollectorMention(source=SourceType.WEB, keyword="example", engagement=3)
    assert mention.engagement == 3

"""
Report generator for OSINT data.
"""
from typing import List, Dict, Any
import json
from datetime import datetime


class ReportGenerator:
    """Generate reports from OSINT data."""
    
    def __init__(self):
        """Initialize the report generator."""
        pass
    
    def generate_summary(self, mentions: List[Dict[str, Any]], 
                        sentiment_stats: Dict[str, Any]) -> str:
        """
        Generate a text summary report.
        
        Args:
            mentions: List of mentions
            sentiment_stats: Sentiment statistics
            
        Returns:
            Formatted text report
        """
        report = []
        report.append("=" * 60)
        report.append("OSINT MONITORING REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Overview
        report.append("OVERVIEW")
        report.append("-" * 60)
        report.append(f"Total Mentions: {sentiment_stats.get('total', 0)}")
        report.append("")
        
        # Sentiment breakdown
        report.append("SENTIMENT ANALYSIS")
        report.append("-" * 60)
        report.append(f"Positive: {sentiment_stats.get('positive', 0)} ({sentiment_stats.get('positive_pct', 0):.1f}%)")
        report.append(f"Negative: {sentiment_stats.get('negative', 0)} ({sentiment_stats.get('negative_pct', 0):.1f}%)")
        report.append(f"Neutral:  {sentiment_stats.get('neutral', 0)} ({sentiment_stats.get('neutral_pct', 0):.1f}%)")
        report.append(f"Average Polarity: {sentiment_stats.get('avg_polarity', 0):.3f}")
        report.append("")
        
        # Source breakdown
        sources = {}
        for mention in mentions:
            source = mention.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        
        report.append("SOURCES")
        report.append("-" * 60)
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            report.append(f"{source}: {count}")
        report.append("")
        
        # Recent mentions
        report.append("RECENT MENTIONS (TOP 5)")
        report.append("-" * 60)
        for i, mention in enumerate(mentions[:5], 1):
            report.append(f"\n{i}. [{mention.get('source', 'unknown')}] by {mention.get('author', 'unknown')}")
            text = mention.get('text', '')
            report.append(f"   {text[:100]}{'...' if len(text) > 100 else ''}")
            sentiment_data = mention.get('sentiment', {})
            if sentiment_data:
                report.append(f"   Sentiment: {sentiment_data.get('sentiment', 'N/A')} (polarity: {sentiment_data.get('polarity', 0):.2f})")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def generate_json(self, mentions: List[Dict[str, Any]], 
                     sentiment_stats: Dict[str, Any]) -> str:
        """
        Generate a JSON report.
        
        Args:
            mentions: List of mentions
            sentiment_stats: Sentiment statistics
            
        Returns:
            JSON formatted report
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": sentiment_stats,
            "mentions": mentions
        }
        
        return json.dumps(report, indent=2, default=str)
    
    def save_report(self, content: str, filename: str):
        """
        Save report to file.
        
        Args:
            content: Report content
            filename: Output filename
        """
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

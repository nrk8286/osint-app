"""FastAPI REST API for OSINT monitoring platform."""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio

from osint_app.core.monitor import OSINTMonitor
from osint_app.models.schemas import Mention, SearchQuery, SourceType
from osint_app.storage.database import DatabaseStorage
from osint_app.core.config import config

# Create FastAPI app
app = FastAPI(
    title="OSINT Monitoring Platform API",
    description="Production-ready OSINT monitoring and data collection API",
    version="2.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global monitor instance
monitor = OSINTMonitor(use_database=True, enable_sentiment=True)
db = DatabaseStorage()


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "OSINT Monitoring Platform API",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": {
            "search": "/api/search",
            "mentions": "/api/mentions",
            "stats": "/api/stats",
            "health": "/health",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    sources_status = {name: source.is_available() for name, source in monitor.sources.items()}

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "sources": sources_status,
        "database": bool(db),
        "sentiment_analysis": bool(monitor.sentiment_analyzer),
    }


@app.post("/api/search", response_model=List[Mention])
async def search(query: SearchQuery, background_tasks: BackgroundTasks):
    """Search for mentions across all sources.

    Args:
        query: Search query parameters

    Returns:
        List of mentions found
    """
    try:
        mentions = await monitor.collect_mentions(
            keyword=query.keyword,
            google_results=query.google_results if query.enable_google else 0,
            twitter_results=query.twitter_results if query.enable_twitter else 0,
            reddit_results=query.reddit_results if query.enable_reddit else 0,
            news_results=query.news_results if query.enable_news else 0,
            enable_sentiment=query.enable_sentiment,
        )

        return mentions

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/mentions", response_model=List[Mention])
async def get_mentions(
    keyword: Optional[str] = None,
    source: Optional[SourceType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Retrieve mentions from database with filtering.

    Args:
        keyword: Filter by keyword
        source: Filter by source type
        start_date: Filter by start date
        end_date: Filter by end date
        limit: Maximum results
        offset: Results offset

    Returns:
        List of mentions
    """
    try:
        mentions = db.get_mentions(
            keyword=keyword,
            source=source,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )
        return mentions

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_statistics(days: int = Query(7, ge=1, le=365)):
    """Get statistics for collected mentions.

    Args:
        days: Number of days to analyze

    Returns:
        Statistics dictionary
    """
    try:
        stats = db.get_stats(days=days)
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sources")
async def get_sources():
    """Get status of all data sources.

    Returns:
        Dictionary of source statuses
    """
    return {
        name: {"available": source.is_available(), "name": source.name, "enabled": source.enabled}
        for name, source in monitor.sources.items()
    }


@app.delete("/api/mentions")
async def clear_old_mentions(days: int = Query(30, ge=1)):
    """Clear mentions older than specified days.

    Args:
        days: Keep mentions newer than this many days

    Returns:
        Number of mentions deleted
    """
    try:
        count = db.clear_old_mentions(days=days)
        return {"deleted": count, "days": days}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze/sentiment")
async def analyze_sentiment(text: str):
    """Analyze sentiment of provided text.

    Args:
        text: Text to analyze

    Returns:
        Sentiment analysis result
    """
    if not monitor.sentiment_analyzer:
        raise HTTPException(status_code=503, detail="Sentiment analysis not available")

    try:
        sentiment, confidence = monitor.sentiment_analyzer.analyze(text)

        return {
            "text": text[:100] + "..." if len(text) > 100 else text,
            "sentiment": sentiment.value if sentiment else None,
            "confidence": confidence,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=config.api_host, port=config.api_port, workers=config.api_workers)

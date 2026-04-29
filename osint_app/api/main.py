"""FastAPI REST API for OSINT monitoring platform."""

from datetime import datetime
from typing import List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from osint_app.core.config import config
from osint_app.core.monitor import OSINTMonitor
from osint_app.models.schemas import Mention, ReconResult, SearchQuery, SourceType
from osint_app.recon.network import NetworkRecon
from osint_app.storage.database import DatabaseStorage

# Create FastAPI app
app = FastAPI(
    title="OSINT Monitoring Platform API",
    description="Production-ready OSINT monitoring, data collection, and reconnaissance API",
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

# Global instances
monitor = OSINTMonitor(use_database=True, enable_sentiment=True)
db = DatabaseStorage()
recon = NetworkRecon()


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
            "sources": "/api/sources",
            "recon_dns": "/api/recon/dns/{domain}",
            "recon_ip": "/api/recon/ip/{target}",
            "recon_headers": "/api/recon/headers",
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


@app.post("/api/search")
async def search(query: SearchQuery):
    """Search for mentions across all sources."""
    try:
        mentions = await monitor.collect_mentions(
            keyword=query.keyword,
            google_results=query.google_results if query.enable_google else 0,
            twitter_results=query.twitter_results if query.enable_twitter else 0,
            reddit_results=query.reddit_results if query.enable_reddit else 0,
            news_results=query.news_results if query.enable_news else 0,
            github_results=query.github_results if query.enable_github else 0,
            enable_sentiment=query.enable_sentiment,
        )
        return {"count": len(mentions), "mentions": [m.model_dump(mode="json") for m in mentions]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/mentions")
async def get_mentions(
    keyword: Optional[str] = None,
    source: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Retrieve mentions from database with filtering."""
    try:
        source_type = SourceType(source) if source else None
        mentions = db.get_mentions(
            keyword=keyword,
            source=source_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )
        return [m.model_dump(mode="json") for m in mentions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_statistics(days: int = Query(7, ge=1, le=365)):
    """Get statistics for collected mentions."""
    try:
        return db.get_stats(days=days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sources")
async def get_sources():
    """Get status of all data sources."""
    return {
        name: {"available": source.is_available(), "name": source.name, "enabled": source.enabled}
        for name, source in monitor.sources.items()
    }


@app.delete("/api/mentions")
async def clear_old_mentions(days: int = Query(30, ge=1)):
    """Clear mentions older than specified days."""
    try:
        count = db.clear_old_mentions(days=days)
        return {"deleted": count, "days": days}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Reconnaissance endpoints ──────────────────────────────────────────


@app.get("/api/recon/dns/{domain}")
async def recon_dns(domain: str):
    """Perform DNS lookup on a domain."""
    result = recon.dns_lookup(domain)
    return result.model_dump(mode="json")


@app.get("/api/recon/ip/{target}")
async def recon_ip(target: str):
    """Get IP geolocation and ISP information."""
    result = recon.ip_info(target)
    return result.model_dump(mode="json")


class HeaderCheckRequest(BaseModel):
    url: str


@app.post("/api/recon/headers")
async def recon_headers(req: HeaderCheckRequest):
    """Analyze HTTP response headers for security assessment."""
    result = recon.check_headers(req.url)
    return result.model_dump(mode="json")


@app.post("/api/analyze/sentiment")
async def analyze_sentiment(text: str):
    """Analyze sentiment of provided text."""
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

"""Vercel serverless entry point for the OSINT Monitoring Platform API."""

import os
import sys
import socket
import re
import json
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
from collections import Counter

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ConfigDict, Field

# ── Pydantic schemas (self-contained for Vercel) ──────────────────────

class SourceType(str, Enum):
    GOOGLE = "google"
    TWITTER = "twitter"
    REDDIT = "reddit"
    NEWS = "news"
    GITHUB = "github"
    WEB = "web"


class SentimentScore(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class Mention(BaseModel):
    model_config = ConfigDict(extra="allow")
    source: SourceType
    keyword: str
    url: str = ""
    title: str = ""
    content: str = ""
    timestamp: str = ""
    author: Optional[str] = None
    relevance_score: Optional[float] = None
    engagement: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchQuery(BaseModel):
    keyword: str
    github_results: int = 10
    enable_github: bool = True


class ReconResult(BaseModel):
    model_config = ConfigDict(extra="allow")
    target: str
    recon_type: str
    timestamp: str = ""
    data: Dict[str, Any] = Field(default_factory=dict)


class HeaderCheckRequest(BaseModel):
    url: str


# ── GitHub search (works without API key) ─────────────────────────────

try:
    import requests as req_lib
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


def search_github(keyword: str, max_results: int = 10) -> List[Mention]:
    if not REQUESTS_AVAILABLE:
        return []
    try:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "OSINT-Monitor/2.0",
        }
        token = os.getenv("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"token {token}"
        resp = req_lib.get(
            "https://api.github.com/search/repositories",
            headers=headers,
            params={"q": keyword, "per_page": min(max_results, 30), "sort": "stars"},
            timeout=15,
        )
        resp.raise_for_status()
        mentions = []
        for repo in resp.json().get("items", []):
            mentions.append(Mention(
                source=SourceType.GITHUB,
                keyword=keyword,
                url=repo.get("html_url", ""),
                title=repo.get("full_name", ""),
                content=repo.get("description", "") or "",
                timestamp=repo.get("updated_at", datetime.now().isoformat()),
                engagement=repo.get("stargazers_count", 0) + repo.get("forks_count", 0),
                metadata={
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "language": repo.get("language"),
                    "topics": repo.get("topics", []),
                },
            ))
        return mentions
    except Exception:
        return []


# ── Recon functions ───────────────────────────────────────────────────

SECURITY_HEADERS = [
    "Strict-Transport-Security", "Content-Security-Policy",
    "X-Content-Type-Options", "X-Frame-Options",
    "X-XSS-Protection", "Referrer-Policy",
    "Permissions-Policy", "Cross-Origin-Opener-Policy",
]


def dns_lookup(domain: str) -> ReconResult:
    domain = re.sub(r"^https?://", "", domain).split("/")[0]
    records: Dict = {}
    try:
        hostname, aliases, addresses = socket.gethostbyname_ex(domain)
        records["hostname"] = hostname
        records["aliases"] = aliases
        records["addresses"] = addresses
    except socket.gaierror as e:
        records["error"] = str(e)
    if records.get("addresses"):
        try:
            rev = socket.gethostbyaddr(records["addresses"][0])
            records["reverse_dns"] = rev[0]
        except Exception:
            pass
    return ReconResult(target=domain, recon_type="dns", timestamp=datetime.now().isoformat(), data=records)


def ip_info(target: str) -> ReconResult:
    if not REQUESTS_AVAILABLE:
        return ReconResult(target=target, recon_type="ip_info", timestamp=datetime.now().isoformat(), data={"error": "requests not available"})
    clean = re.sub(r"^https?://", "", target).split("/")[0]
    try:
        ip = socket.gethostbyname(clean)
    except socket.gaierror:
        ip = clean
    try:
        resp = req_lib.get(f"http://ip-api.com/json/{ip}", timeout=10)
        data = resp.json()
    except Exception as e:
        data = {"error": str(e)}
    return ReconResult(target=ip, recon_type="ip_info", timestamp=datetime.now().isoformat(), data=data)


def check_headers(url: str) -> ReconResult:
    if not REQUESTS_AVAILABLE:
        return ReconResult(target=url, recon_type="headers", timestamp=datetime.now().isoformat(), data={"error": "requests not available"})
    if not url.startswith("http"):
        url = f"https://{url}"
    try:
        resp = req_lib.head(url, headers={"User-Agent": "OSINT-Monitor/2.0"}, timeout=10, allow_redirects=True)
        security = {h: resp.headers.get(h) for h in SECURITY_HEADERS}
        data = {
            "status_code": resp.status_code,
            "server": resp.headers.get("Server"),
            "security_headers": security,
            "present": [h for h, v in security.items() if v],
            "missing": [h for h, v in security.items() if not v],
        }
    except Exception as e:
        data = {"error": str(e)}
    return ReconResult(target=url, recon_type="headers", timestamp=datetime.now().isoformat(), data=data)


# ── Relevance scoring ────────────────────────────────────────────────

def calc_relevance(keyword: str, text: str) -> float:
    if not text:
        return 0.0
    kw = keyword.lower()
    words = text.lower().split()
    occ = text.lower().count(kw)
    return round(min(occ / max(len(words), 1) * 10, 1.0), 2)


# ── In-memory store ──────────────────────────────────────────────────

mention_store: List[Mention] = []
search_history: List[dict] = []


# ── FastAPI app ──────────────────────────────────────────────────────

app = FastAPI(
    title="OSINT Monitoring Platform",
    description="Production-ready OSINT monitoring, search, and reconnaissance API",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Dashboard ────────────────────────────────────────────────────────

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OSINT Monitoring Platform</title>
<style>
  :root { --bg: #0f172a; --card: #1e293b; --accent: #38bdf8; --green: #4ade80; --red: #f87171; --yellow: #fbbf24; --text: #e2e8f0; --dim: #94a3b8; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', system-ui, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }
  .container { max-width: 1100px; margin: 0 auto; padding: 20px; }
  header { text-align: center; padding: 30px 0 20px; }
  header h1 { font-size: 2rem; color: var(--accent); }
  header p { color: var(--dim); margin-top: 5px; }
  .tabs { display: flex; gap: 8px; margin: 20px 0; flex-wrap: wrap; }
  .tab { padding: 10px 20px; border-radius: 8px; background: var(--card); color: var(--dim); border: 1px solid transparent; cursor: pointer; font-size: 0.9rem; transition: all 0.2s; }
  .tab.active, .tab:hover { color: var(--accent); border-color: var(--accent); }
  .panel { display: none; } .panel.active { display: block; }
  .card { background: var(--card); border-radius: 12px; padding: 24px; margin-bottom: 16px; }
  .card h3 { color: var(--accent); margin-bottom: 12px; font-size: 1.1rem; }
  .form-row { display: flex; gap: 10px; margin-bottom: 12px; flex-wrap: wrap; }
  input, select { background: var(--bg); border: 1px solid #334155; color: var(--text); padding: 10px 14px; border-radius: 8px; font-size: 0.9rem; }
  input:focus, select:focus { outline: none; border-color: var(--accent); }
  input[type=text], input[type=url], input[type=number] { flex: 1; min-width: 200px; }
  button { background: var(--accent); color: var(--bg); border: none; padding: 10px 24px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 0.9rem; transition: opacity 0.2s; }
  button:hover { opacity: 0.85; } button:disabled { opacity: 0.5; cursor: not-allowed; }
  .results { margin-top: 16px; }
  .result-item { background: var(--bg); border-radius: 8px; padding: 14px; margin-bottom: 8px; border-left: 3px solid var(--accent); }
  .result-item .source { display: inline-block; background: var(--accent); color: var(--bg); padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
  .result-item .title { font-weight: 600; margin: 6px 0 4px; }
  .result-item .url { color: var(--dim); font-size: 0.8rem; word-break: break-all; }
  .result-item .meta { color: var(--dim); font-size: 0.8rem; margin-top: 4px; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; margin-right: 6px; }
  .badge.present { background: rgba(74,222,128,0.15); color: var(--green); }
  .badge.missing { background: rgba(248,113,113,0.15); color: var(--red); }
  .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 16px; }
  .stat-card { background: var(--bg); border-radius: 8px; padding: 16px; text-align: center; }
  .stat-card .value { font-size: 2rem; font-weight: 700; color: var(--accent); }
  .stat-card .label { color: var(--dim); font-size: 0.8rem; margin-top: 4px; }
  .loading { text-align: center; padding: 20px; color: var(--dim); }
  .loading::after { content: ''; display: inline-block; width: 18px; height: 18px; border: 2px solid var(--accent); border-top-color: transparent; border-radius: 50%; animation: spin 0.8s linear infinite; margin-left: 8px; vertical-align: middle; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .empty { text-align: center; padding: 40px; color: var(--dim); }
  @media (max-width: 600px) { .form-row { flex-direction: column; } input[type=text] { min-width: auto; } }
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>OSINT Monitoring Platform</h1>
    <p>v2.0 &mdash; Search &bull; Reconnaissance &bull; Analysis</p>
  </header>

  <div class="tabs">
    <div class="tab active" data-tab="search">Search</div>
    <div class="tab" data-tab="recon">Recon</div>
    <div class="tab" data-tab="headers">Headers</div>
    <div class="tab" data-tab="history">History</div>
    <div class="tab" data-tab="about">API Docs</div>
  </div>

  <!-- SEARCH -->
  <div id="search" class="panel active">
    <div class="card">
      <h3>Search GitHub Repositories</h3>
      <div class="form-row">
        <input type="text" id="searchKeyword" placeholder="Enter keyword (e.g. cybersecurity, OSINT)">
        <input type="number" id="searchLimit" value="10" min="1" max="30" style="width:80px;flex:none">
        <button onclick="doSearch()">Search</button>
      </div>
      <div id="searchResults"></div>
    </div>
  </div>

  <!-- RECON -->
  <div id="recon" class="panel">
    <div class="card">
      <h3>Domain / IP Reconnaissance</h3>
      <div class="form-row">
        <input type="text" id="reconTarget" placeholder="Domain or IP (e.g. example.com)">
        <button onclick="doRecon()">Lookup</button>
      </div>
      <div id="reconResults"></div>
    </div>
  </div>

  <!-- HEADERS -->
  <div id="headers" class="panel">
    <div class="card">
      <h3>HTTP Security Header Analysis</h3>
      <div class="form-row">
        <input type="url" id="headerUrl" placeholder="URL (e.g. https://example.com)">
        <button onclick="doHeaders()">Analyze</button>
      </div>
      <div id="headerResults"></div>
    </div>
  </div>

  <!-- HISTORY -->
  <div id="history" class="panel">
    <div class="card">
      <h3>Search History &amp; Collected Mentions</h3>
      <div class="stats-grid" id="statsGrid"></div>
      <div id="historyResults"><p class="empty">Run a search to see results here.</p></div>
    </div>
  </div>

  <!-- ABOUT -->
  <div id="about" class="panel">
    <div class="card">
      <h3>API Endpoints</h3>
      <div class="result-item"><b>POST</b> /api/search &mdash; Search GitHub repos by keyword</div>
      <div class="result-item"><b>GET</b> /api/recon/dns/{domain} &mdash; DNS lookup</div>
      <div class="result-item"><b>GET</b> /api/recon/ip/{target} &mdash; IP geolocation</div>
      <div class="result-item"><b>POST</b> /api/recon/headers &mdash; HTTP header analysis</div>
      <div class="result-item"><b>GET</b> /api/mentions &mdash; List stored mentions</div>
      <div class="result-item"><b>GET</b> /api/stats &mdash; Summary statistics</div>
      <div class="result-item"><b>GET</b> /health &mdash; Health check</div>
      <div class="result-item"><b>GET</b> /docs &mdash; Interactive Swagger UI</div>
    </div>
  </div>
</div>

<script>
const BASE = '';
let allMentions = [];

// Tabs
document.querySelectorAll('.tab').forEach(t => t.addEventListener('click', () => {
  document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(x => x.classList.remove('active'));
  t.classList.add('active');
  document.getElementById(t.dataset.tab).classList.add('active');
}));

function loading(id) { document.getElementById(id).innerHTML = '<div class="loading">Loading</div>'; }

function renderMention(m) {
  const eng = m.engagement ? ` | Engagement: ${m.engagement}` : '';
  const rel = m.relevance_score ? ` | Relevance: ${m.relevance_score}` : '';
  const stars = m.metadata?.stars != null ? ` | Stars: ${m.metadata.stars}` : '';
  const lang = m.metadata?.language ? ` | ${m.metadata.language}` : '';
  return `<div class="result-item">
    <span class="source">${m.source}</span>
    <div class="title">${m.title || 'Untitled'}</div>
    <div class="url"><a href="${m.url}" target="_blank" style="color:inherit">${m.url}</a></div>
    ${m.content ? `<div class="meta">${m.content.slice(0,150)}</div>` : ''}
    <div class="meta">${m.timestamp}${stars}${lang}${eng}${rel}</div>
  </div>`;
}

async function doSearch() {
  const kw = document.getElementById('searchKeyword').value.trim();
  const limit = parseInt(document.getElementById('searchLimit').value) || 10;
  if (!kw) return;
  loading('searchResults');
  try {
    const res = await fetch(BASE + '/api/search', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({keyword:kw, github_results:limit}) });
    const data = await res.json();
    const mentions = data.mentions || [];
    allMentions = allMentions.concat(mentions);
    if (mentions.length === 0) { document.getElementById('searchResults').innerHTML = '<p class="empty">No results found.</p>'; return; }
    document.getElementById('searchResults').innerHTML = `<p style="color:var(--green);margin-bottom:12px">Found ${mentions.length} result(s)</p>` + mentions.map(renderMention).join('');
    updateHistory();
  } catch(e) { document.getElementById('searchResults').innerHTML = `<p style="color:var(--red)">Error: ${e.message}</p>`; }
}

async function doRecon() {
  const target = document.getElementById('reconTarget').value.trim();
  if (!target) return;
  loading('reconResults');
  try {
    const [dns, ip] = await Promise.all([
      fetch(BASE + `/api/recon/dns/${encodeURIComponent(target)}`).then(r=>r.json()),
      fetch(BASE + `/api/recon/ip/${encodeURIComponent(target)}`).then(r=>r.json()),
    ]);
    let html = '<h4 style="color:var(--accent);margin:12px 0 8px">DNS Records</h4>';
    if (dns.data.error) { html += `<div class="result-item"><span style="color:var(--red)">${dns.data.error}</span></div>`; }
    else {
      html += `<div class="result-item">
        <div><b>Hostname:</b> ${dns.data.hostname||'N/A'}</div>
        <div><b>Addresses:</b> ${(dns.data.addresses||[]).join(', ')||'N/A'}</div>
        <div><b>Aliases:</b> ${(dns.data.aliases||[]).join(', ')||'None'}</div>
        ${dns.data.reverse_dns ? `<div><b>Reverse DNS:</b> ${dns.data.reverse_dns}</div>` : ''}
      </div>`;
    }
    html += '<h4 style="color:var(--accent);margin:12px 0 8px">IP Geolocation</h4>';
    if (ip.data.error) { html += `<div class="result-item"><span style="color:var(--red)">${ip.data.error}</span></div>`; }
    else if (ip.data.status === 'success') {
      html += `<div class="result-item">
        <div><b>IP:</b> ${ip.target}</div>
        <div><b>Country:</b> ${ip.data.country||'N/A'} (${ip.data.countryCode||''})</div>
        <div><b>Region:</b> ${ip.data.regionName||'N/A'}</div>
        <div><b>City:</b> ${ip.data.city||'N/A'}</div>
        <div><b>ISP:</b> ${ip.data.isp||'N/A'}</div>
        <div><b>Org:</b> ${ip.data.org||'N/A'}</div>
        <div><b>AS:</b> ${ip.data.as||'N/A'}</div>
      </div>`;
    } else { html += `<div class="result-item">${JSON.stringify(ip.data)}</div>`; }
    document.getElementById('reconResults').innerHTML = html;
  } catch(e) { document.getElementById('reconResults').innerHTML = `<p style="color:var(--red)">Error: ${e.message}</p>`; }
}

async function doHeaders() {
  const url = document.getElementById('headerUrl').value.trim();
  if (!url) return;
  loading('headerResults');
  try {
    const res = await fetch(BASE + '/api/recon/headers', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({url}) });
    const data = await res.json();
    if (data.data.error) { document.getElementById('headerResults').innerHTML = `<div class="result-item" style="color:var(--red)">${data.data.error}</div>`; return; }
    let html = `<div class="result-item"><b>Status:</b> ${data.data.status_code} | <b>Server:</b> ${data.data.server||'N/A'}</div>`;
    html += '<div style="margin-top:12px">';
    const sec = data.data.security_headers || {};
    for (const [h, v] of Object.entries(sec)) {
      if (v) html += `<span class="badge present">+ ${h}</span>`;
      else html += `<span class="badge missing">- ${h}</span>`;
    }
    html += '</div>';
    const missing = data.data.missing || [];
    if (missing.length) html += `<p style="color:var(--yellow);margin-top:12px">${missing.length} security header(s) missing</p>`;
    else html += `<p style="color:var(--green);margin-top:12px">All security headers present!</p>`;
    document.getElementById('headerResults').innerHTML = html;
  } catch(e) { document.getElementById('headerResults').innerHTML = `<p style="color:var(--red)">Error: ${e.message}</p>`; }
}

function updateHistory() {
  const grid = document.getElementById('statsGrid');
  const sources = {};
  allMentions.forEach(m => { sources[m.source] = (sources[m.source]||0) + 1; });
  grid.innerHTML = `<div class="stat-card"><div class="value">${allMentions.length}</div><div class="label">Total Mentions</div></div>` +
    Object.entries(sources).map(([s,c]) => `<div class="stat-card"><div class="value">${c}</div><div class="label">${s}</div></div>`).join('');
  document.getElementById('historyResults').innerHTML = allMentions.length ? allMentions.map(renderMention).join('') : '<p class="empty">No results yet.</p>';
}
</script>
</body>
</html>"""


# ── Routes ───────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the OSINT dashboard UI."""
    return DASHBOARD_HTML


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "sources": {"github": True, "dns": True, "ip_info": REQUESTS_AVAILABLE, "headers": REQUESTS_AVAILABLE},
    }


@app.post("/api/search")
async def search(query: SearchQuery):
    mentions = []
    if query.enable_github:
        mentions = search_github(query.keyword, query.github_results)
    for m in mentions:
        m.relevance_score = calc_relevance(query.keyword, f"{m.title} {m.content}")
    # Deduplicate
    seen = set()
    unique = []
    for m in mentions:
        if m.url not in seen:
            seen.add(m.url)
            unique.append(m)
    mention_store.extend(unique)
    search_history.append({"keyword": query.keyword, "timestamp": datetime.now().isoformat(), "results": len(unique)})
    return {"count": len(unique), "mentions": [m.model_dump() for m in unique]}


@app.get("/api/mentions")
async def get_mentions(
    keyword: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
):
    results = mention_store
    if keyword:
        results = [m for m in results if m.keyword.lower() == keyword.lower()]
    if source:
        results = [m for m in results if m.source.value.lower() == source.lower()]
    return [m.model_dump() for m in results[:limit]]


@app.get("/api/stats")
async def stats():
    sources = Counter(m.source.value for m in mention_store)
    keywords = Counter(m.keyword for m in mention_store)
    return {
        "total_mentions": len(mention_store),
        "by_source": dict(sources),
        "by_keyword": dict(keywords.most_common(10)),
        "searches": len(search_history),
    }


@app.get("/api/recon/dns/{domain}")
async def recon_dns(domain: str):
    return dns_lookup(domain).model_dump()


@app.get("/api/recon/ip/{target}")
async def recon_ip(target: str):
    return ip_info(target).model_dump()


@app.post("/api/recon/headers")
async def recon_headers(req: HeaderCheckRequest):
    return check_headers(req.url).model_dump()

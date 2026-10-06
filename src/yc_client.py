"""Ultra-fast Y Combinator client for Algolia API and SSR detail enrichment.
Browserless, zero-proxy, high-performance data extraction.
"""
import asyncio
import html
import json
import logging
import re
import urllib.parse
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger("yc_client")

# Official Algolia endpoints and public search keys
ALGOLIA_APP_ID = "45BWZJ1SGC"
ALGOLIA_QUERIES_URL = "https://45BWZJ1SGC-dsn.algolia.net/1/indexes/*/queries"

COMPANY_INDEX = "YCCompany_production"
FOUNDER_INDEX = "YCUsers_production"

COMPANY_SEARCH_KEY = (
    "NzJmMWExZWYxYzY5OGYwN2VkYWM5YzRiM2VlNDFlM2I0ODU2YjQ2Yjg0MTFiNWE5NzY0NTMyZGI1OWEwMzVjY2FuYWx5dGljc1RhZ3M9eWNkYyZyZXN0cmljdEluZGljZXM9WUNDb21wYW55X3Byb2R1Y3Rpb24lMkNZQ0NvbXBhbnlfQnlfTGF1bmNoX0RhdGVfcHJvZHVjdGlvbiZ0YWdGaWx0ZXJzPSU1QiUyMnljZGNfcHVibGljJTIyJTVE"
)
FOUNDER_SEARCH_KEY = (
    "Mjg1MjYxZmI3ZWQ5YTNjZjg3M2VkNzg5NzNhOTI3MjljMGY2Zjc4YzI2YmI0MzFlYTk5ZWU4ODM1NzQ1MzIwN2FuYWx5dGljc1RhZ3M9eWNkYyZyZXN0cmljdEluZGljZXM9WUNVc2Vyc19wcm9kdWN0aW9uJnRhZ0ZpbHRlcnM9JTVCJTIyeWNkY19wdWJsaWMlMjIlNUQ="
)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def sanitize_data(val: Any) -> Any:
    """Sanitize strings by replacing em-dashes and en-dashes with hyphens."""
    if isinstance(val, str):
        return val.replace("\u2014", " - ").replace("\u2013", "-")
    elif isinstance(val, list):
        return [sanitize_data(x) for x in val]
    elif isinstance(val, dict):
        return {k: sanitize_data(v) for k, v in val.items()}
    return val


def batch_to_short(batch_name: str) -> str:
    """Convert 'Winter 2026' to 'W26', 'Summer 2025' to 'S25', etc."""
    batch_name = batch_name.strip()
    m = re.match(r"^(Summer|Winter|Fall|Spring)\s+(20\d\d|\d\d)$", batch_name, re.IGNORECASE)
    if m:
        season, year = m.groups()
        s_code = {"summer": "S", "winter": "W", "fall": "F", "spring": "P"}[season.lower()]
        return f"{s_code}{year[-2:]}"
    return batch_name


class YCClient:
    """High-performance client for Y Combinator directory and founder data."""

    def __init__(self, timeout: float = 15.0, max_concurrency: int = 15):
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrency)
        limits = httpx.Limits(max_connections=35, max_keepalive_connections=20)
        self.client = httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=timeout, limits=limits)

    async def close(self):
        """Close HTTP client connection pool."""
        await self.client.aclose()

    async def get_all_batches(self) -> List[str]:
        """Fetch list of all available YC batches from Algolia facets."""
        headers = {
            "x-algolia-application-id": ALGOLIA_APP_ID,
            "x-algolia-api-key": COMPANY_SEARCH_KEY,
            "Content-Type": "application/json",
        }
        payload = {
            "requests": [
                {
                    "indexName": COMPANY_INDEX,
                    "params": "hitsPerPage=1&facets=[\"batch\"]",
                }
            ]
        }
        try:
            resp = await self.client.post(ALGOLIA_QUERIES_URL, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                facets = data["results"][0].get("facets", {}).get("batch", {})
                # Return batches sorted chronologically descending
                return sorted(list(facets.keys()), reverse=True)
        except Exception as e:
            logger.warning(f"Failed to fetch batch facets: {e}")
        return []

    async def query_algolia(
        self,
        index_name: str,
        api_key: str,
        params_str: str,
    ) -> List[Dict[str, Any]]:
        """Execute a single Algolia query request."""
        headers = {
            "x-algolia-application-id": ALGOLIA_APP_ID,
            "x-algolia-api-key": api_key,
            "Content-Type": "application/json",
        }
        payload = {"requests": [{"indexName": index_name, "params": params_str}]}
        try:
            resp = await self.client.post(ALGOLIA_QUERIES_URL, headers=headers, json=payload)
            if resp.status_code == 200:
                result = resp.json()["results"][0]
                return result.get("hits", [])
            else:
                logger.error(f"Algolia error: HTTP {resp.status_code} - {resp.text[:200]}")
        except Exception as e:
            logger.error(f"Algolia request exception: {e}")
        return []

    async def fetch_companies(
        self,
        query: str = "",
        batches: Optional[List[str]] = None,
        industries: Optional[List[str]] = None,
        status: str = "all",
        is_hiring: bool = False,
        top_company: bool = False,
        max_items: int = 100,
    ) -> List[Dict[str, Any]]:
        """Fetch YC companies matching criteria.
        Handles Algolia 1000 item limit by partitioning queries across batches when needed.
        """
        batches = batches or []
        industries = industries or []

        # If specific batches are requested, query each batch
        if batches:
            collected: List[Dict[str, Any]] = []
            seen_ids = set()
            for b in batches:
                if len(collected) >= max_items:
                    break
                p = self._build_company_params(
                    query=query,
                    batch=b,
                    industries=industries,
                    status=status,
                    is_hiring=is_hiring,
                    top_company=top_company,
                    hits_per_page=1000,
                    page=0,
                )
                hits = await self.query_algolia(COMPANY_INDEX, COMPANY_SEARCH_KEY, p)
                for h in hits:
                    hid = h.get("id")
                    if hid not in seen_ids:
                        seen_ids.add(hid)
                        collected.append(h)
                        if len(collected) >= max_items:
                            break
            return collected[:max_items]

        # No specific batches requested:
        # If max_items <= 1000, single fast query
        if max_items <= 1000:
            p = self._build_company_params(
                query=query,
                industries=industries,
                status=status,
                is_hiring=is_hiring,
                top_company=top_company,
                hits_per_page=max_items,
                page=0,
            )
            hits = await self.query_algolia(COMPANY_INDEX, COMPANY_SEARCH_KEY, p)
            return hits[:max_items]

        # max_items > 1000: Partition across all 51 batches to extract full dataset
        all_batches = await self.get_all_batches()
        if not all_batches:
            # Fallback to single page
            p = self._build_company_params(
                query=query,
                industries=industries,
                status=status,
                is_hiring=is_hiring,
                top_company=top_company,
                hits_per_page=1000,
                page=0,
            )
            return await self.query_algolia(COMPANY_INDEX, COMPANY_SEARCH_KEY, p)

        collected = []
        seen_ids = set()
        for b in all_batches:
            if len(collected) >= max_items:
                break
            p = self._build_company_params(
                query=query,
                batch=b,
                industries=industries,
                status=status,
                is_hiring=is_hiring,
                top_company=top_company,
                hits_per_page=1000,
                page=0,
            )
            hits = await self.query_algolia(COMPANY_INDEX, COMPANY_SEARCH_KEY, p)
            for h in hits:
                hid = h.get("id")
                if hid not in seen_ids:
                    seen_ids.add(hid)
                    collected.append(h)
                    if len(collected) >= max_items:
                        break
        return collected[:max_items]

    def _build_company_params(
        self,
        query: str = "",
        batch: Optional[str] = None,
        industries: Optional[List[str]] = None,
        status: str = "all",
        is_hiring: bool = False,
        top_company: bool = False,
        hits_per_page: int = 100,
        page: int = 0,
    ) -> str:
        """Construct encoded Algolia params for company query."""
        params: Dict[str, Any] = {
            "hitsPerPage": hits_per_page,
            "page": page,
            "query": query.strip() if query else "",
        }
        facet_filters: List[Any] = []
        if batch:
            facet_filters.append([f"batch:{batch}"])
        if industries:
            facet_filters.append([f"industry:{ind}" for ind in industries])
        if status and status != "all":
            facet_filters.append([f"status:{status}"])
        if is_hiring:
            facet_filters.append(["isHiring:true"])
        if top_company:
            facet_filters.append(["top_company:true"])

        if facet_filters:
            params["facetFilters"] = json.dumps(facet_filters)

        return urllib.parse.urlencode(params)

    async def fetch_company_detail(self, slug: str) -> Dict[str, Any]:
        """Fetch deep details and founder social links from company SSR page."""
        if not slug:
            return {}
        url = f"https://www.ycombinator.com/companies/{slug}"
        async with self.semaphore:
            try:
                resp = await self.client.get(url)
                if resp.status_code != 200:
                    return {}
                match = re.search(r'data-page="([^"]+)"', resp.text)
                if not match:
                    return {}
                data_str = html.unescape(match.group(1))
                page_data = json.loads(data_str)
                return page_data.get("props", {}).get("company", {})
            except Exception as e:
                logger.debug(f"Detail fetch failed for {slug}: {e}")
                return {}

    async def enrich_companies(
        self,
        companies: List[Dict[str, Any]],
        concurrency: int = 15,
    ) -> List[Dict[str, Any]]:
        """Concurrently enrich company records with deep SSR detail."""
        logger.info(f"Enriching {len(companies)} companies with deep details...")
        tasks = [self.fetch_company_detail(c.get("slug", "")) for c in companies]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        enriched: List[Dict[str, Any]] = []
        for raw_c, detail in zip(companies, results):
            detail_dict = detail if isinstance(detail, dict) else {}
            normalized = self.normalize_company(raw_c, detail_dict)
            enriched.append(normalized)
        return enriched

    def normalize_company(
        self,
        hit: Dict[str, Any],
        detail: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Normalize company hit and optional detail props into clean schema."""
        detail = detail or {}

        # Parse founders from detail props
        founders_data = []
        raw_founders = detail.get("founders", []) or []
        for f in raw_founders:
            founders_data.append({
                "name": f.get("full_name", ""),
                "title": f.get("title", ""),
                "linkedin_url": f.get("linkedin_url"),
                "twitter_url": f.get("twitter_url"),
                "avatar_thumb": f.get("avatar_thumb_url"),
                "bio": f.get("founder_bio"),
                "is_active": f.get("is_active", True),
            })

        # Derive year founded
        year_founded = detail.get("year_founded")
        if not year_founded and hit.get("launched_at"):
            try:
                # launched_at is often unix timestamp
                import datetime
                year_founded = str(datetime.datetime.fromtimestamp(int(hit["launched_at"])).year)
            except Exception:
                year_founded = None

        res = {
            "id": hit.get("id"),
            "name": hit.get("name"),
            "slug": hit.get("slug"),
            "website": detail.get("website") or hit.get("website"),
            "one_liner": detail.get("one_liner") or hit.get("one_liner"),
            "long_description": detail.get("long_description") or hit.get("long_description"),
            "batch": hit.get("batch") or detail.get("batch_name"),
            "status": hit.get("status") or detail.get("ycdc_status", "Active"),
            "stage": hit.get("stage"),
            "team_size": detail.get("team_size") or hit.get("team_size"),
            "year_founded": year_founded,
            "location": detail.get("location") or hit.get("all_locations"),
            "city": detail.get("city"),
            "country": detail.get("country"),
            "regions": hit.get("regions", []),
            "industry": hit.get("industry"),
            "subindustry": hit.get("subindustry"),
            "tags": hit.get("tags", []),
            "top_company": bool(hit.get("top_company", False)),
            "isHiring": bool(hit.get("isHiring", False)),
            "small_logo_thumb_url": hit.get("small_logo_thumb_url") or detail.get("small_logo_url"),
            "linkedin_url": detail.get("linkedin_url"),
            "twitter_url": detail.get("twitter_url"),
            "github_url": detail.get("github_url"),
            "crunchbase_url": detail.get("cb_url"),
            "founders": founders_data,
        }
        return sanitize_data(res)

    async def fetch_founders(
        self,
        query: str = "",
        batches: Optional[List[str]] = None,
        industries: Optional[List[str]] = None,
        top_company: bool = False,
        max_items: int = 100,
    ) -> List[Dict[str, Any]]:
        """Fetch YC founders from Algolia YCUsers_production index."""
        batches = batches or []
        industries = industries or []

        params: Dict[str, Any] = {
            "hitsPerPage": min(max_items, 1000),
            "page": 0,
            "query": query.strip() if query else "",
        }
        facet_filters: List[Any] = []
        if batches:
            short_batches = [batch_to_short(b) for b in batches]
            facet_filters.append([f"batches:{b}" for b in short_batches])
        if industries:
            facet_filters.append([f"yc_parent_industries:{ind}" for ind in industries])
        if top_company:
            facet_filters.append(["top_company:true"])

        if facet_filters:
            params["facetFilters"] = json.dumps(facet_filters)

        encoded_params = urllib.parse.urlencode(params)
        hits = await self.query_algolia(FOUNDER_INDEX, FOUNDER_SEARCH_KEY, encoded_params)

        normalized_founders: List[Dict[str, Any]] = []
        for h in hits[:max_items]:
            first_name = h.get("first_name", "")
            last_name = h.get("last_name", "")
            full_name = f"{first_name} {last_name}".strip()
            slug = h.get("url_slug") or ""
            linkedin_url = f"https://www.linkedin.com/in/{slug}/" if slug else None

            normalized_founders.append({
                "id": h.get("id"),
                "first_name": first_name,
                "last_name": last_name,
                "full_name": full_name,
                "current_company": h.get("current_company"),
                "company_slug": h.get("company_slug"),
                "current_title": h.get("current_title") or (h.get("yc_titles", [None])[0] if h.get("yc_titles") else None),
                "batches": h.get("batches", []),
                "linkedin_url": linkedin_url,
                "twitter_url": None,
                "avatar_thumb": h.get("avatar_thumb"),
                "regions": h.get("current_region"),
                "top_company": bool(h.get("top_company", False)),
            })

        return sanitize_data(normalized_founders)

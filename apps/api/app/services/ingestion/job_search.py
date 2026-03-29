import asyncio
import logging
from dataclasses import dataclass

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class JobSearchResult:
    title: str
    company: str
    location: str | None
    description: str | None
    url: str | None
    source_api: str


async def search_adzuna(query: str, location: str = "") -> list[JobSearchResult]:
    """Search Adzuna API. Returns empty list on failure."""
    if not settings.ADZUNA_APP_ID or not settings.ADZUNA_APP_KEY:
        return []

    try:
        params = {
            "app_id": settings.ADZUNA_APP_ID,
            "app_key": settings.ADZUNA_APP_KEY,
            "results_per_page": 10,
            "what": query,
        }
        if location:
            params["where"] = location

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://api.adzuna.com/v1/api/jobs/us/search/1",
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("results", []):
            results.append(JobSearchResult(
                title=item.get("title", ""),
                company=item.get("company", {}).get("display_name", "Unknown"),
                location=item.get("location", {}).get("display_name"),
                description=item.get("description"),
                url=item.get("redirect_url"),
                source_api="adzuna",
            ))
        return results
    except Exception as e:
        logger.warning(f"Adzuna search failed: {e}")
        return []


async def search_jooble(query: str, location: str = "") -> list[JobSearchResult]:
    """Search Jooble API. Returns empty list on failure."""
    if not settings.JOOBLE_API_KEY:
        return []

    try:
        body = {"keywords": query}
        if location:
            body["location"] = location

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"https://jooble.org/api/{settings.JOOBLE_API_KEY}",
                json=body,
            )
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("jobs", []):
            results.append(JobSearchResult(
                title=item.get("title", ""),
                company=item.get("company", "Unknown"),
                location=item.get("location"),
                description=item.get("snippet"),
                url=item.get("link"),
                source_api="jooble",
            ))
        return results
    except Exception as e:
        logger.warning(f"Jooble search failed: {e}")
        return []


async def search_jsearch(query: str, location: str = "") -> list[JobSearchResult]:
    """Search JSearch via RapidAPI. Returns empty list on failure."""
    if not settings.RAPIDAPI_KEY:
        return []

    try:
        search_query = f"{query} in {location}" if location else query

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://jsearch.p.rapidapi.com/search",
                params={"query": search_query, "page": "1", "num_pages": "1"},
                headers={
                    "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
                    "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("data", []):
            loc_parts = [item.get("job_city"), item.get("job_state")]
            location_str = ", ".join(p for p in loc_parts if p) or None

            results.append(JobSearchResult(
                title=item.get("job_title", ""),
                company=item.get("employer_name", "Unknown"),
                location=location_str,
                description=item.get("job_description", "")[:2000],
                url=item.get("job_apply_link"),
                source_api="jsearch",
            ))
        return results
    except Exception as e:
        logger.warning(f"JSearch search failed: {e}")
        return []


async def search_all(query: str, location: str = "") -> list[JobSearchResult]:
    """Aggregate results from all configured APIs with deduplication."""
    tasks = []
    if settings.ADZUNA_APP_ID and settings.ADZUNA_APP_KEY:
        tasks.append(search_adzuna(query, location))
    if settings.JOOBLE_API_KEY:
        tasks.append(search_jooble(query, location))
    if settings.RAPIDAPI_KEY:
        tasks.append(search_jsearch(query, location))

    if not tasks:
        return []

    results_lists = await asyncio.gather(*tasks, return_exceptions=True)

    all_results = []
    for result in results_lists:
        if isinstance(result, list):
            all_results.extend(result)
        elif isinstance(result, Exception):
            logger.warning(f"Job search provider failed: {result}")

    return _deduplicate(all_results)[:20]


def _deduplicate(results: list[JobSearchResult]) -> list[JobSearchResult]:
    """Remove duplicate jobs based on title+company."""
    seen = set()
    unique = []
    for r in results:
        key = (r.title.lower().strip(), r.company.lower().strip())
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique

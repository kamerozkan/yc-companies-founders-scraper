"""Y Combinator Companies & Founders Scraper Actor entrypoint.
Ultra-fast HTTP/REST extraction for YC startups and founders.
"""
import asyncio
import time
from typing import Any, Dict, List

from apify import Actor
from src.yc_client import YCClient


async def main() -> None:
    """Actor main entrypoint."""
    async with Actor:
        # 1. Fetch input with comprehensive default fallbacks for zero-config runs
        actor_input: Dict[str, Any] = await Actor.get_input() or {}

        output_mode: str = actor_input.get("outputMode", "companies")
        search_query: str = str(actor_input.get("searchQuery", "")).strip()

        # Normalize batches input
        raw_batches = actor_input.get("batches") or []
        if isinstance(raw_batches, str):
            batches = [b.strip() for b in raw_batches.split(",") if b.strip()]
        elif isinstance(raw_batches, list):
            batches = [str(b).strip() for b in raw_batches if str(b).strip()]
        else:
            batches = []

        # Normalize industries input
        raw_industries = actor_input.get("industries") or []
        if isinstance(raw_industries, str):
            industries = [i.strip() for i in raw_industries.split(",") if i.strip()]
        elif isinstance(raw_industries, list):
            industries = [str(i).strip() for i in raw_industries if str(i).strip()]
        else:
            industries = []

        status: str = actor_input.get("status", "all")
        is_hiring: bool = bool(actor_input.get("isHiring", False))
        top_company_only: bool = bool(actor_input.get("topCompanyOnly", False))
        include_deep_details: bool = bool(actor_input.get("includeDeepDetails", True))

        try:
            max_items: int = int(actor_input.get("maxItems", 50))
        except (ValueError, TypeError):
            max_items = 50
        if max_items <= 0:
            max_items = 50

        Actor.log.info(
            f"Starting scraper with mode='{output_mode}', query='{search_query}', "
            f"batches={batches}, status='{status}', maxItems={max_items}, "
            f"deepDetails={include_deep_details}"
        )

        start_time = time.time()
        client = YCClient(timeout=20.0, max_concurrency=15)
        pushed_count = 0

        try:
            # Mode 1: Scrape companies
            if output_mode == "companies":
                raw_companies = await client.fetch_companies(
                    query=search_query,
                    batches=batches,
                    industries=industries,
                    status=status,
                    is_hiring=is_hiring,
                    top_company=top_company_only,
                    max_items=max_items,
                )
                Actor.log.info(f"Retrieved {len(raw_companies)} companies from directory index.")

                if include_deep_details and raw_companies:
                    records = await client.enrich_companies(raw_companies)
                else:
                    records = [client.normalize_company(c) for c in raw_companies]

                for record in records:
                    await Actor.push_data(record)
                    pushed_count += 1
                    if hasattr(Actor, "charge"):
                        try:
                            await Actor.charge(event_name="yc-record", count=1)
                        except Exception:
                            pass

            # Mode 2: Scrape founders
            elif output_mode == "founders":
                founders = await client.fetch_founders(
                    query=search_query,
                    batches=batches,
                    industries=industries,
                    top_company=top_company_only,
                    max_items=max_items,
                )
                Actor.log.info(f"Retrieved {len(founders)} founders from directory index.")

                for record in founders:
                    await Actor.push_data(record)
                    pushed_count += 1
                    if hasattr(Actor, "charge"):
                        try:
                            await Actor.charge(event_name="yc-record", count=1)
                        except Exception:
                            pass

            # Mode 3: Scrape both companies and founders
            elif output_mode == "both":
                half_limit = max(1, max_items // 2)
                raw_companies = await client.fetch_companies(
                    query=search_query,
                    batches=batches,
                    industries=industries,
                    status=status,
                    is_hiring=is_hiring,
                    top_company=top_company_only,
                    max_items=half_limit,
                )
                if include_deep_details and raw_companies:
                    comp_records = await client.enrich_companies(raw_companies)
                else:
                    comp_records = [client.normalize_company(c) for c in raw_companies]

                for r in comp_records:
                    r["itemType"] = "company"
                    await Actor.push_data(r)
                    pushed_count += 1
                    if hasattr(Actor, "charge"):
                        try:
                            await Actor.charge(event_name="yc-record", count=1)
                        except Exception:
                            pass

                founders = await client.fetch_founders(
                    query=search_query,
                    batches=batches,
                    industries=industries,
                    top_company=top_company_only,
                    max_items=max_items - pushed_count,
                )
                for f in founders:
                    f["itemType"] = "founder"
                    await Actor.push_data(f)
                    pushed_count += 1
                    if hasattr(Actor, "charge"):
                        try:
                            await Actor.charge(event_name="yc-record", count=1)
                        except Exception:
                            pass

        except Exception as e:
            Actor.log.error(f"Error executing scraper: {e}")
            raise
        finally:
            await client.close()

        elapsed = time.time() - start_time
        rate = pushed_count / elapsed if elapsed > 0 else 0
        summary_msg = f"Extracted {pushed_count} records in {elapsed:.2f}s ({rate:.1f} records/s)"
        Actor.log.info(summary_msg)
        await Actor.set_status_message(summary_msg)


if __name__ == "__main__":
    asyncio.run(main())

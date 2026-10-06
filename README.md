# Y Combinator Companies & Founders Scraper

Ultra-fast, browserless scraper for the complete **Y Combinator** directory (`ycombinator.com/companies` and `ycombinator.com/founders`). Extract verified company intelligence, tech tags, funding status, hiring signals, and founder LinkedIn profiles directly via official APIs.

---

## Why Use This Scraper?

- **70% Cheaper than Alternatives**: Priced at just **$0.003 per result** ($3.00 / 1,000 records) compared to legacy competitors charging $10.00+ per 1k records.
- **Zero Browser Automation**: Pure lightweight HTTP requests (50ms response times) delivering >99% compute efficiency.
- **No 1,000-Item Pagination Wall**: Automatically partitions queries across all 51 YC batches to extract the entire 6,270+ company and 13,900+ founder database without missing records.
- **Deep Social & Founder Enrichment**: Automatically extracts founder LinkedIn URLs, X / Twitter profiles, bios, and company social handles.
- **Console-Ready Table Views**: Visual Apify Console tables with company logos and clickable links.

---

## Output Modes

1. **Companies (Default)**: Full company metadata, hiring status, team metrics, and array of associated founders with LinkedIn links.
2. **Founders**: Individual founder profiles with role, company, YC batch, and direct social URLs.
3. **Both**: Combines company records and founder records in a single dataset.

---

## Input Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `outputMode` | String | `"companies"` | Choose `"companies"`, `"founders"`, or `"both"`. |
| `searchQuery` | String | `""` | Keyword search (e.g. `"artificial intelligence"`, `"fintech"`, `"compliance"`). |
| `batches` | Array | `[]` | Filter by specific batches (e.g. `["Winter 2026", "Summer 2025"]`). Empty for all. |
| `industries` | Array | `[]` | Filter by industry (e.g. `["B2B", "Fintech", "Healthcare"]`). |
| `status` | String | `"all"` | Filter by status: `"all"`, `"Active"`, `"Acquired"`, `"Inactive"`, `"Public"`. |
| `isHiring` | Boolean | `false` | When true, only returns companies with active open positions. |
| `topCompanyOnly` | Boolean | `false` | When true, only returns top valued YC companies (e.g. Stripe, Airbnb). |
| `includeDeepDetails` | Boolean | `true` | When true, enriches records with founder LinkedIn links and company socials. |
| `maxItems` | Integer | `50` | Maximum number of records to extract. Set higher for full directory sync. |

---

## Sample Output (Company Record)

```json
{
  "id": 240,
  "name": "Stripe",
  "slug": "stripe",
  "website": "http://stripe.com",
  "one_liner": "Economic infrastructure for the internet.",
  "long_description": "Stripe is a global technology company that builds economic infrastructure for the internet.",
  "batch": "Summer 2009",
  "status": "Active",
  "stage": "Growth",
  "team_size": 7000,
  "year_founded": "2009",
  "location": "San Francisco, CA, USA",
  "city": "San Francisco",
  "country": "US",
  "regions": [
    "United States of America",
    "America / Canada"
  ],
  "industry": "Fintech",
  "subindustry": "Fintech",
  "tags": [
    "Banking as a Service",
    "Fintech",
    "SaaS"
  ],
  "top_company": true,
  "isHiring": true,
  "small_logo_thumb_url": "https://bookface-images.s3.amazonaws.com/small_logos/e5ccedd9995f6524b4a0379062eb67f7c991613e.png",
  "linkedin_url": "https://www.linkedin.com/company/stripe/",
  "twitter_url": "https://twitter.com/stripe",
  "github_url": "https://github.com/stripe",
  "crunchbase_url": "https://www.crunchbase.com/organization/stripe",
  "founders": [
    {
      "name": "Patrick Collison",
      "title": "Founder/CEO",
      "linkedin_url": "https://www.linkedin.com/in/patrickcollison/",
      "twitter_url": "https://twitter.com/patrickc",
      "avatar_thumb": "https://bookface-images.s3.amazonaws.com/avatars/...",
      "bio": "",
      "is_active": true
    },
    {
      "name": "John Collison",
      "title": "Founder/President",
      "linkedin_url": "https://www.linkedin.com/in/johnbcollison/",
      "twitter_url": "https://twitter.com/collision",
      "avatar_thumb": "https://bookface-images.s3.amazonaws.com/avatars/...",
      "bio": "",
      "is_active": true
    }
  ]
}
```

---

## Pricing Model (Pay-Per-Event)

- **$0.003 per extracted record** ($3.00 per 1,000 results).
- Zero monthly subscription required.
- Zero proxy fees or bandwidth surcharges.

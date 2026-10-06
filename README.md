# Y Combinator Scraper & Startup Leads API (Companies & Founders)

<p align="center">
  <img src="https://apify-image-uploads-prod.s3.us-east-1.amazonaws.com/IgeKo3nNKdc47C5AT-actor-wHFYMA8uTMrmdhjfK-ZBHM8lvgoh-Y_Combinator_logo.svg.png" width="128" height="128" alt="Y Combinator Logo" style="border-radius: 24px;" />
</p>

[![Run on Apify](https://apify.com/actor-badge?actor=kamerozkan/yc-companies-founders-scraper)](https://apify.com/kamerozkan/yc-companies-founders-scraper)
[![Apify Actor](https://img.shields.io/badge/Apify-Actor-blue.svg)](https://apify.com/kamerozkan/yc-companies-founders-scraper)

[![Pricing](https://img.shields.io/badge/Pricing-$0.003%20/%20record-green.svg)](https://apify.com/kamerozkan/yc-companies-founders-scraper)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-brightgreen.svg)](https://apify.com/kamerozkan/yc-companies-founders-scraper)

Ultra-fast, browserless scraper and real-time data API for the complete **Y Combinator** startup ecosystem (`ycombinator.com/companies` and `ycombinator.com/founders`). Extract verified company intelligence, tech tags, team metrics, hiring signals, and founder LinkedIn profiles directly via official endpoints.

---

## Who Buys and Uses This Actor?

- **Venture Capital & Angel Investors**: Spot emerging stealth startups before demo day. Filter by cohort, industry (AI, Fintech, Bio), or location to power automated dealflow pipelines.
- **B2B Outbound Sales & SDR Teams**: Connect with well-funded founders holding fresh capital. Obtain verified founder LinkedIn URLs and active hiring signals to time your outreach perfectly.
- **Executive Recruiters & Talent Agencies**: Track fast-growing YC startups with active job openings (`isHiring: true`) to source high-paying candidate placements.
- **Market Intelligence & Corporate Development**: Map tech stacks, market trends, team sizing, and alumni networks across 51 YC cohorts from W05 to W26.

---

## Why Choose This Scraper?

- **70% Cheaper than Legacy Scrapers**: Priced at flat **$0.003 per extracted record** ($3.00 per 1,000 results). No monthly retainer or recurring subscription required.
- **Zero Browser Overhead**: Built on pure, asynchronous HTTP requests with sub-50ms query times. Runs efficiently on only 128 MB to 256 MB RAM.
- **No 1,000-Item Pagination Wall**: YC search interfaces cap results at 1,000 records per search query. This scraper automatically partitions historical batches across all 51 cohorts, letting you export the entire 6,270+ company and 13,900+ founder database without missing a single company.
- **Deep Social & Founder Enrichment**: Captures founder LinkedIn URLs, X / Twitter profiles, avatar photos, company socials (GitHub, Twitter, LinkedIn, Crunchbase), and active hiring flags.
- **Console-Ready Table Views**: Pre-configured visual Apify Console table views with company logos and clickable web links.

---

## Output Modes

1. **Companies (`outputMode: "companies"`)**: Full company profile, funding batch, industry tags, hiring status, team size, and an array of verified founders with LinkedIn URLs.
2. **Founders (`outputMode: "founders"`)**: Individual founder profiles with current titles, company affiliations, cohort batches, and direct LinkedIn profile links.
3. **Both (`outputMode: "both"`)**: Combines company records and founder records in a single dataset with an `itemType` field.

---

## Input Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `outputMode` | String | `"companies"` | Output format: `"companies"`, `"founders"`, or `"both"`. |
| `searchQuery` | String | `""` | Keyword search across company name, one-liner, and description (e.g. `"artificial intelligence"`, `"fintech"`). |
| `batches` | Array | `[]` | Filter by YC batch cohorts (e.g. `["Winter 2026", "Summer 2025"]`). Leave empty for all batches. |
| `industries` | Array | `[]` | Filter by industry (e.g. `["B2B", "Fintech", "Healthcare", "Consumer"]`). |
| `status` | String | `"all"` | Operational status: `"all"`, `"Active"`, `"Acquired"`, `"Inactive"`, `"Public"`. |
| `isHiring` | Boolean | `false` | When true, returns only startups with active job openings. |
| `topCompanyOnly` | Boolean | `false` | When true, filters to top-tier YC companies (e.g. Stripe, Airbnb, DoorDash, Coinbase). |
| `includeDeepDetails` | Boolean | `true` | Enriches company records with founder LinkedIn links, bios, and company social handles. |
| `maxItems` | Integer | `50` | Maximum number of records to return. Increase for bulk syncs. |

---

## JSON Input Examples

### Example 1: Active AI Companies Hiring Now
```json
{
  "outputMode": "companies",
  "searchQuery": "artificial intelligence",
  "status": "Active",
  "isHiring": true,
  "includeDeepDetails": true,
  "maxItems": 100
}
```

### Example 2: Recent Cohort Founder Outreach Pipeline
```json
{
  "outputMode": "founders",
  "batches": ["Winter 2026", "Summer 2025"],
  "industries": ["B2B", "Fintech"],
  "maxItems": 250
}
```

---

## JSON Output Examples

### Company Record (`outputMode: "companies"`)
```json
{
  "id": 240,
  "name": "Stripe",
  "slug": "stripe",
  "website": "http://stripe.com",
  "one_liner": "Economic infrastructure for the internet.",
  "long_description": "Stripe is a technology company that builds economic infrastructure for the internet. Businesses of every size use our software to accept payments and manage their businesses online.",
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
    "Fintech",
    "Payments",
    "SaaS",
    "B2B"
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
      "avatar_thumb": "https://bookface-images.s3.amazonaws.com/avatars/240.png",
      "bio": "Co-founder and CEO of Stripe.",
      "is_active": true
    },
    {
      "name": "John Collison",
      "title": "Founder/President",
      "linkedin_url": "https://www.linkedin.com/in/johnbcollison/",
      "twitter_url": "https://twitter.com/collision",
      "avatar_thumb": "https://bookface-images.s3.amazonaws.com/avatars/241.png",
      "bio": "Co-founder and President of Stripe.",
      "is_active": true
    }
  ]
}
```

### Founder Record (`outputMode: "founders"`)
```json
{
  "id": 14210,
  "first_name": "Patrick",
  "last_name": "Collison",
  "full_name": "Patrick Collison",
  "current_company": "Stripe",
  "company_slug": "stripe",
  "current_title": "Co-Founder and CEO",
  "batches": [
    "S09"
  ],
  "linkedin_url": "https://www.linkedin.com/in/patrickcollison/",
  "twitter_url": null,
  "avatar_thumb": "https://bookface-images.s3.amazonaws.com/avatars/240.png",
  "regions": "San Francisco Bay Area",
  "top_company": true
}
```

---

## Step-by-Step No-Code Integration Guides

Connect Y Combinator intelligence directly into your daily dealflow, outbound prospecting, or CRM stack without writing custom code.

### 1. Google Sheets (Live Data Sync)
Sync freshly funded YC startups into your Google Spreadsheet automatically:
- **Instant Formula**: In cell `A1` of any Google Sheet, paste:
  ```excel
  =IMPORTDATA("https://api.apify.com/v2/datasets/{DATASET_ID}/items?format=csv&clean=1")
  ```
  *(Replace `{DATASET_ID}` with the dataset ID from your Actor run).*
- **Scheduled Sync via Apify**: Go to the **Integrations** tab of this Actor in Apify Console, select **Google Sheets**, and connect your target spreadsheet. New records will append automatically on every scheduled batch run.

### 2. Make.com (CRM & Slack Notifications)
Set up automated alerts for newly funded companies:
1. Create a new scenario in Make.com and add the **Apify: Run Actor** module.
2. Select `kamerozkan/yc-companies-founders-scraper` and configure your search filter (e.g. `status = "Active"`, `isHiring = true`).
3. Add a **Filter** step: Keep records where `industry = "Fintech"` or `isHiring = true`.
4. Add a **HubSpot / Salesforce / Notion** module: Create new company and contact records with founder LinkedIn profile URLs.
5. Add a **Slack** module: Post high-priority dealflow alerts into your `#dealflow-alerts` channel.

### 3. n8n Workflow (Cold Outbound Prospecting)
Automate founder outreach sequences:
1. In n8n, add an **Apify Node** triggered by a schedule (e.g. every Monday morning).
2. Set `outputMode` to `"founders"` with your target YC batches (e.g. `["Winter 2026"]`).
3. Pass the founder list into an email verification node or data enrichment service (Clay, Hunter, Apollo).
4. Auto-enroll verified founder contacts into your cold outreach platform (Instantly, Smartlead).

### 4. Webhooks (Real-Time Backend Push)
Send extracted data straight to your custom API or webhook endpoint upon run completion:
1. In the Apify Actor console, navigate to the **Integrations** tab.
2. Click **Add Webhook** and paste your webhook endpoint URL (e.g. `https://api.yourcompany.com/webhooks/yc-leads`).
3. Select the trigger event: `ACTOR.RUN.SUCCEEDED`.
4. Your server will receive an HTTP POST request containing the run metadata and dataset URL as soon as the run finishes.

---

## Automated Weekly Schedule (Recurring Retention Recipe)

Do not run scrapers manually every time Y Combinator updates. Set up an automated weekly schedule to keep your pipeline continuously refreshed with newly funded startups and founders:

1. **Open the Schedules Tab**: In your Apify Console, navigate to **Schedules** > **Create new schedule**.
2. **Set Cron Expression**: Choose **Every Monday at 08:00 UTC** (`0 8 * * 1`) to receive fresh deals at the start of every business week.
3. **Select Actor**: Choose `kamerozkan/yc-companies-founders-scraper` and configure your target criteria (e.g. `status: "Active"`, `isHiring: true`, `outputMode: "companies"`).
4. **Auto-Sync to Google Sheets / CRM**: Under the Actor's **Integrations** tab, select **Google Sheets** (or webhook to HubSpot/Salesforce). New weekly records will automatically append to your live spreadsheet.
5. **Team Alerts**: Connect Slack integration to ping your `#dealflow` or `#sales-leads` channel every Monday morning with the newly extracted startups.

This automated recipe transforms one-off data exports into a continuous, hands-off dealflow engine for your investment or sales team.

---

## Pay-Per-Event Pricing Value Proposition

| Feature | Legacy Scrapers / Directories | This Apify Actor |
|---|---|---|
| **Pricing Model** | $49 to $199 / month subscription | **Pay-Per-Event ($0.003 / record)** |
| **Cost for 1,000 Startups** | $10.00 to $25.00 | **$3.00 flat** |
| **Cost for 10,000 Records** | $100.00+ | **$30.00 flat** |
| **Proxy / Bandwidth Fees** | Billed separately ($5 to $15 / GB) | **$0.00 (Zero proxy costs)** |
| **Browser Compute Surcharges**| High (1GB to 4GB RAM required) | **$0.00 (Browserless 128MB RAM)** |
| **YC Pagination Limit Bypass** | Capped at 1,000 results | **Full 51-batch partitioning** |
| **Founder LinkedIn Enrichment** | Paid add-on ($0.05 / contact) | **Included free in every record** |

Zero recurring subscription fees. You only pay for the exact volume of startup and founder records you extract.

---

## Developer Quickstart & Organic Search Engine Keywords

Target high-intent search terms: `y combinator companies scraper github`, `yc founder dataset`, `y combinator api`, `yc dealflow scraper`, `scrape y combinator`, `y combinator linkedin extractor`.

### Python Quickstart
```python
from apify_client import ApifyClient

# Initialize client with your Apify API token
client = ApifyClient("YOUR_APIFY_TOKEN")

# Configure scraper input
run_input = {
    "outputMode": "companies",
    "searchQuery": "fintech",
    "status": "Active",
    "isHiring": True,
    "maxItems": 50,
}

# Run scraper actor
run = client.actor("kamerozkan/yc-companies-founders-scraper").call(run_input=run_input)

# Fetch and print results
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(f"{item['name']} ({item['batch']}) - {item.get('website')}")
```

### Node.js / JavaScript Quickstart
```javascript
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({
    token: 'YOUR_APIFY_TOKEN',
});

const input = {
    outputMode: 'companies',
    searchQuery: 'artificial intelligence',
    isHiring: true,
    maxItems: 50,
};

const run = await client.actor('kamerozkan/yc-companies-founders-scraper').call(input);
const { items } = await client.dataset(run.defaultDatasetId).listItems();
console.log(`Retrieved ${items.length} YC companies.`);
```

### Direct cURL Command
```bash
curl -X POST "https://api.apify.com/v2/acts/kamerozkan~yc-companies-founders-scraper/runs?token=YOUR_APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"outputMode": "companies", "searchQuery": "ai", "maxItems": 50}'
```

---

## Frequently Asked Questions

**Does this scraper require residential proxies?**
No. All requests query direct structured API endpoints without browser automation or aggressive bot challenges. You incur zero proxy bandwidth expenses.

**How do you handle YC pagination limits?**
The Y Combinator web frontend caps search queries at 1,000 items. This Actor automatically partitions requests across all 51 historical cohorts (W05 to W26), allowing you to extract all 6,270+ companies and 13,900+ founders without data truncation.

**Can I extract only founder profiles?**
Yes. Set `outputMode` to `"founders"` to extract individual founder records containing full names, current roles, company slugs, and verified LinkedIn URLs.

**How up-to-date is the startup data?**
Data is fetched live during every run directly from Y Combinator directory indices. As soon as a startup launches on YC or an existing company updates hiring status, your next run captures the latest changes immediately.

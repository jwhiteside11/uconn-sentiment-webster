# Data fetching service for the Sentiment project

This subfolder holds all of the code to:
1. Scrape financial news from Yahoo finance and store in Datastore.
2. Get news stories directly from Datastore.
3. Search news data using Typesense.

The code is designed to run on the Compute Engine VM. This subfolder uses Docker to containerize different parts of the application. We will have one container for the Typesense server, and one for the Python code herein.

# Quick start

To run the `data-fetchers` locally, it is easiest to just run the full application locally using `docker compose`.

```bash
# from root folder
docker compose -f docker-compose-local.yml up
```

Everything is now up and running. Test it by logging into the `auth-server`.
```bash
curl -X POST 'localhost:5100/auth/authenticate' -H "Content-Type: application/json" -d '{"username": "testuser": "password123"}'
```

This will return a passkey. The passkey is needed for requests to the API.
```bash
curl 'localhost:5100/api' -H "WBS-API-PASSKEY: ..."
```

**Note:** if the build environment changes, the Typesense server must be backfilled with the news we've scraped into datastore. After the first build, the index will be stored in the attached container volume. There is an endpoint for backfilling after the first build.
```bash
curl 'localhost:5100/api/backfill_typesense' -H "WBS-API-PASSKEY: ..."
```

## Authentication

Every request to `data-fetchers` must provide a valid passkey as a cookie or a header with the key `WBS-API-PASSKEY`. Requests with missing or invalid tokens are returned an error message.

To retrieve a token, one must log in using the `auth-server`. See the example in [Quick start](#quick-start) for more info.

# API reference
This code is wrapped with a Flask server. Interact with this code base using HTTP calls to `localhost:5100`. 

In the examples above, I use the `curl` shell command, but you can interface with the containers any HTTP library in any language.

## Endpoints

### GET /scrape_news

Scrape news from Yahoo Finance using Selenium and requests.

#### Request
- **Method**: GET
- **URL**: `/scrape_news`

#### Query Parameters
| Parameter    | Type   | Description                        |
|--------------|--------|------------------------------------|
| `ticker`       | str    | The ticker of the company of interest (required). |

#### Example Request
`curl 'localhost:5100/api/scrape_news?ticker=WBS' -H "WBS-API-PASSKEY: ..."`

#### Response
- **Status Code**: 200 OK
- **Content-Type**: `application/json`

```json
{
  "num_attempts": 4, 
  "num_success": 3, 
  "results": [
    {"message": "success: https://finance.yahoo.com/news/curious-webster-financial-wbs-q4-141510242.html"},
    {"message": "failed: already scraped url https://finance.yahoo.com/news/webster-financial-corporation-wbs-best-093505383.html"},
    {"message": "success: https://finance.yahoo.com/news/webster-financials-nyse-wbs-dividend-120809687.html"},
    {"message": "success: https://finance.yahoo.com/news/earnings-preview-webster-financial-wbs-150010712.html"},
  ]
}
```
---

### GET /search_news

Search for news using Typesense server.

#### Request
- **Method**: GET
- **URL**: `/search_news`

#### Query Parameters
| Parameter    | Type   | Description                        |
|--------------|--------|------------------------------------|
| `ticker`       | str    | The ticker of the company of interest (required). |
| `search_term`  | str    | The word/phrase to search for (required). |

#### Example Request
`curl 'localhost:5100/api/search_news?ticker=WBS&search_term=bank' -H "WBS-API-PASSKEY: ..."`

#### Response
- **Status Code**: 200 OK
- **Content-Type**: `application/json`

```json
{
  "num_hits": 1, 
  "hits": [
    {
      "highlights": [
        "holding company for Webster <mark>Bank</mark> would post earnings of",
        "belongs to the Zacks <mark>Bank</mark>s - Northeast industry, posted revenues",
        "the Zacks Industry Rank, <mark>Bank</mark>s - Northeast is currently in"
      ],
      "magnitude": 7.303900000000001,
      "score": 0.05226564407348633,
      "title": "Webster Financial (WBS) Q4 Earnings Top Estimates",
      "url": "https://finance.yahoo.com/news/webster-financial-wbs-q4-earnings-134004111.html"
    }
  ]
}
```
---

### GET /score_news

Score all news stories for a ticker using sentiment model.

#### Request
- **Method**: GET
- **URL**: `/score_news`

#### Query Parameters
| Parameter    | Type   | Description                        |
|--------------|--------|------------------------------------|
| `ticker`       | str    | The ticker of the company of interest (required). |

#### Example Request
`curl 'localhost:5100/api/score_news?ticker=WBS' -H "WBS-API-PASSKEY: ..."`

#### Response
- **Status Code**: 200 OK
- **Content-Type**: `application/json`

```json
[
  {"message": "SUCCESS https://finance.yahoo.com/news/webster-financial-wbs-q4-earnings-134004111.html score: 0.05226564407348633 magnitude: 7.303900000000001"},
  {"message": "ERROR <some unexpected system error...>"}
]
```
---

### GET /backfill_typesense

Backfill Typesense server with news articles from Datastore. It will skip the documents already found in the index.

#### Request
- **Method**: GET
- **URL**: `/backfill_typesense`

#### Query Parameters
| Parameter    | Type   | Description                        |
|--------------|--------|------------------------------------|
| `ticker`       | str    | The ticker of the company of interest (optional; if not provided, evrey news document in the Datastore will be indexed). |

#### Example Request
`curl 'localhost:5100/api/backfill_typesense?ticker=WBS' -H "WBS-API-PASSKEY: ..."`

#### Response
- **Status Code**: 200 OK
- **Content-Type**: `application/json`

```json
{
  "num_found": 26,
  "num_indexed": 16
}
```
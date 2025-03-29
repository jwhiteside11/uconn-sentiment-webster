# Data fetching service for the Sentiment project

This subfolder holds all of the code to:
1. Scrape financial news from Yahoo finance and store in Datastore.
2. Get news stories directly from Datastore.
3. Search news data using Typesense.

The code is designed to run on the Compute Engine VM. This subfolder uses Docker to containerize different parts of the application. We will have one container for the Typesense server, and one for the Python code herein.

# Quick start

First, SSH into the VM.

From there, pull the code into the VM.
```bash
# if you don't already have the code base on your VM
git clone https://github.com/jwhiteside11/uconn-sentiment-backend.git

# if you DO already have the code, the following will update
git pull https://github.com/jwhiteside11/uconn-sentiment-backend.git
```

Navigate to this subfolder.
```bash
cd uconn-sentiment-backend/data-fetchers
```

From here, we must get Docker up and running. Begin by installing Docker on your VM instance.
```bash
sudo apt install docker.io
```

To run these containers on our VM at the same time, we will use the shell command `tmux`. If you are not already familiar, review [this guide](https://hamvocke.com/blog/a-quick-and-easy-guide-to-tmux/) before proceeding.

Then, we must pull the Typesense image, and run it on our VM. 
```bash
tmux new-session -A -t typesense

# from tmux session
sudo docker pull typesense/typesense:28.0

sudo docker run -p 8108:8108 -v/tmp/data:/data typesense/typesense:28.0 --data-dir /data --api-key=Hu52dwsas2AdxdE
# (Ctrl + B) + D
```

Now, Typesense is up and running in a container, and accessible via HTTP. 

We are going to do pretty much the same for the Python code we wrote, this time using a local Dockerfile.
```bash
tmux new-session -A -t fetch_server

# from tmux session
sudo docker build --tag fetch_server .

sudo docker run --add-host=host.docker.internal:host-gateway -p 5100:5100 fetch_server
# (Ctrl + B) + D
```

So we have two Docker containers up and running. To interact with these services, we can use HTTP calls.

Everything is now up and running. Test the server using the `Hello world!` example.
```bash
curl 'localhost:5100/'
```

**Note:** if the build environment changes, the server must be backfilled with the news we've scraped into datastore. After the first build, the index will be stored in the attached container volume. There is an endpoint for backfilling after the first build.
```bash
curl 'localhost:5100/backfill_typesense'
```

## Authentication

Every request to `data-fetchers` must provide a valid passkey as a cookie or a header with the key `WBS-API-PASSKEY`. Requests with missing or invalid tokens are returned an error message.

To retrieve a token, one must log in using the `auth-server`. See the [API reference](/auth-server#api-reference) for more info.

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
`curl 'localhost:5100/scrape_news?ticker=WBS'`

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
`curl 'localhost:5100/search_news?ticker=WBS&search_term=bank'`

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
`curl 'localhost:5100/score_news?ticker=WBS'`

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
`curl 'localhost:5100/backfill_typesense?ticker=WBS'`

#### Response
- **Status Code**: 200 OK
- **Content-Type**: `application/json`

```json
{
  "num_found": 26,
  "num_indexed": 16
}
```
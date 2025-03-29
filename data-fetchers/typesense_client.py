import typesense
import sys

class NewsDocument:
    def __init__(self, ticker: str, date: str, title: str, url: str, paragraphs: list[str], score: float = 0, magnitude: float = 0, id: str = ""):
        self.ticker = ticker
        self.date = date
        self.title = title
        self.url = url
        self.paragraphs = paragraphs
        self.score = score
        self.magnitude = magnitude


class TypesenseClient:
    def __init__(self):
        self.client = typesense.Client({
            'api_key': 'Hu52dwsas2AdxdE',
            'nodes': [{
                'host': 'host.docker.internal',
                'port': '8108',
                'protocol': 'http'
            }],
            'connection_timeout_seconds': 2
        })

    def createNewsCollection(self):
        return self.client.collections.create({
            "name": "news",
            "fields": [
                {"name": "ticker", "type": "string", "facet": True },
                {"name": "date", "type": "string" },
                {"name": "title", "type": "string" },
                {"name": "url", "type": "string" },
                {"name": "paragraphs", "type": "string[]" },
                {"name": "score", "type": "float" },
                {"name": "magnitude", "type": "float" },
            ]
        })

    def createNewsDocument(self, news_doc: NewsDocument):
        return self.client.collections['news'].documents.create({**news_doc.__dict__, "id": news_doc.url})

    def getIndexedURLs(self, ticker: str):
        search_parameters = {
            'q'         : "*",
            'query_by'  : 'title',
            'filter_by' : f'ticker:={ticker}',
            'include_fields': 'url, score, magnitude'
        }
        try:
            res = self.client.collections['news'].documents.search(search_parameters)
            condensed = {
                "num_hits": res["found"], 
                "urls": [hit["document"]["url"] for hit in res["hits"]]
            }
            return condensed
        except Exception as e:
            return {"message": f"ERROR {e}"}

    def getIndexedTickers(self):
        search_parameters = {
            'q'         : "*",
            'query_by'  : 'title',
            'facet_by' : 'ticker',
            'include_fields': 'ticker',
            'page': 1,
            'per_page': 25
        }
        try:
            res = self.client.collections['news'].documents.search(search_parameters)
            condensed = {
                "num_hits": res["facet_counts"][0]["stats"]["total_values"], 
                "tickers": [{"count": hit["count"], "value": hit["value"]} for hit in res["facet_counts"][0]["counts"]]
            }
            return condensed
        except Exception as e:
            return {"message": f"ERROR {e}"}

    def getScoresByTicker(self, ticker: str):
        search_parameters = {
            'q'         : "*",
            'query_by'  : 'title',
            'filter_by' : f'ticker:={ticker}',
            'include_fields': 'date, url, score, magnitude',
            'page': 1,
            'per_page': 50
        }
        try:
            res = self.client.collections['news'].documents.search(search_parameters)
            condensed = {
                "num_hits": res["found"], 
                "documents": [hit["document"] for hit in res["hits"]]
            }
            return condensed
        except Exception as e:
            return {"message": f"ERROR {e}"}

    def searchNews(self, ticker: str, search_term: str):
        search_parameters = {
            'q'         : "*" if search_term is None else search_term,
            'query_by'  : 'paragraphs',
            'highlight_fields': 'paragraphs',
            'filter_by' : f'ticker:={ticker}',
            'include_fields': 'url, title, score, magnitude'
        }
        try:
            res = self.client.collections['news'].documents.search(search_parameters)
            condensed = {
                "num_hits": res["found"], 
                "hits": [{
                    "title": hit["document"]["title"], 
                    "url": hit["document"]["url"], 
                    "score": hit["document"]["score"],
                    "magnitude": hit["document"]["magnitude"],
                    "highlights": [] if "paragraphs" not in hit["highlight"] else [p["snippet"] for p in hit["highlight"]["paragraphs"] if len(p["matched_tokens"]) > 0]
                } for hit in res["hits"]]
            }
            return condensed
        except Exception as e:
            return {"message": f"ERROR {e}"}

    def deleteNewsColletion(self):
        return self.client.collections['news'].delete()
        


def run_program(ticker, search_term):
    # Create client
    ts = TypesenseClient()

    # Search documents
    res = ts.searchNews(ticker, search_term)
    print(res)

def test_program():
    # 1) Create client
    ts = TypesenseClient()

    # 2) Create collection
    ts.createNewsCollection()

    # 3) Add some documents
    doc1 = NewsDocument("WBS", "August 20, 2024", "Microsoft's dominant 21st century offers a key lesson for stock market investors: Morning Brief", "https://finance.yahoo.com/news/microsofts-dominant-21st-century-offers-a-key-lesson-for-stock-market-investors-morning-brief-100009433.html", 
                        [
                            "This is The Takeaway from today's Morning Brief, which you can sign up to receive in your inbox every morning along with:",
                            "Economic data releases and earnings",
                            "When the economic cycle actually turns, the biggest drivers of the stock market will change.",
                            "An obvious statement, perhaps. But the current market rebound is being led by the same handful of Big Tech winners that have dominated both returns and the market conversation since 2023.",
                            "And until these terms and conditions change, this remains the AI moment.",
                        ])

    ts.createNewsDocument(doc1)

    # 4) Search documents
    res = ts.searchNews("WBS", "AI")
    print(res)



if __name__ == "__main__":
    ticker = sys.argv[1]
    search_term = sys.argv[2]

    run_program(ticker, search_term)
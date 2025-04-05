import fetch_news
import fetch_utils
import fetch_earnings_calls
from model_client import ModelClient
from datastore_client import DatastoreClient
from auth_client import AuthClient
from typesense_client import TypesenseClient, NewsDocument

class Fetcher:
  def __init__(self):
    self.ds = DatastoreClient()
    self.ts = TypesenseClient()
    self.model = ModelClient()
    self.auth = AuthClient()

  # Scrape Yahoo Finance news stories from the past 2 quarters
  def scrape_news(self, ticker: str):
    past_2_q = fetch_utils.get_past_8_quarters()[:2]

    results = []
    for (y, q) in past_2_q:
      # fetch Yahoo finance urls to scrape
      urls = fetch_news.get_article_urls(ticker, y, q, 25)
      
      # exclude urls that have already been scraped
      indexed = self.ts.getIndexedURLs(ticker)
      if "num_hits" in indexed:
        urls = [url for url in urls if url not in set(indexed["urls"])]

      # scrape each news story
      for url in urls:
        res = fetch_news.scrape_news_story(url)
        if "error" in res:
          print(f"scrape failed: {url}", res['error'])
          results.append({"message": f"ERROR {res['error']}"})
          continue

        print(f"scraped: {url}")
        # score using FinBERT model
        score_res = self.model.score_text('\n'.join(res["paragraphs"]))
        # save document to datastore
        news_doc = NewsDocument(ticker=ticker, score=score_res["score"], magnitude=score_res["magnitude"], **res)
        self.ds.createNewsStoryEntity(news_doc)
        # index into typesense
        try:
          self.ts.createNewsDocument(news_doc)
          print("added: ", news_doc.url)
        except Exception as e:
          print("failed: ", news_doc.url, e)

        results.append({"message": f"SUCCESS {res['url']}"})

    return results

  def score_news(self, ticker: str):
      results = []
      urls = self.ds.getAllNewsDocIDs(ticker)
      
      for url in urls:
        doc = self.ds.getNewsDocByID(url)
        # score using FinBERT model
        score_res = self.model.score_text('\n'.join(doc.paragraphs))
        if "error" in score_res:
          results.append({"messsage": f"ERROR {score_res['error']}"})
        else:
          doc.score = score_res["score"]
          doc.magnitude = score_res["magnitude"]
          # save document to datastore
          self.ds.createNewsStoryEntity(doc)
          results.append({"message": f"SUCCESS {doc.url} score: {doc.score} magnitude: {doc.magnitude}"})
      return results
  

  def scrape_earnings_calls(self, ticker: str):
    past_8_q = fetch_utils.get_past_8_quarters()[2:3]
    
    results = []
    for (y, q) in past_8_q:
      res = fetch_earnings_calls.fetch_earnings_call(ticker, y, q)
      if "error" in res:
        print(f"call pull failed:", res['error'])
        results.append({"message": f"ERROR {res['error']}"})
        continue

      # score using FinBERT model
      transcript = res["result"]["transcript"]
      score_res = self.model.score_text(transcript)
      call = fetch_earnings_calls.EarningsCallTranscript(ticker=ticker, year=y, quarter=q, date=res["date"], paragraphs=transcript.split('\n'), score=score_res["score"], magnitude=score_res["magnitude"])

      # TODO save to datastore, index in typesense
      results.append({"message": f"SUCCESS {res['url']}"})

    return results

  def backfillTypesenseServer(self, ticker: str):
    if ticker is None:
      print("resetting Typesense server")
      self.ts.deleteNewsColletion()
      self.ts.createNewsCollection()
    
    url_res = self.ts.getIndexedURLs(ticker)
    indexed_urls = set(url_res["urls"] if "urls" in url_res else [])
    ids = [id for id in self.ds.getAllNewsDocIDs(ticker) if id not in indexed_urls]
    
    fails = 0
    for id in ids:
      if id in indexed_urls:
        continue

      doc = self.ds.getNewsDocByID(id)
      try:
        self.ts.createNewsDocument(doc)
        print("added: ", doc.url)
      except Exception as e:
        print("failed: ", doc.url)
        fails += 1

    return {"num_found": len(ids), "num_indexed": len(ids) - fails}
    
  def initTypesenseServer(self):
    try:
      self.ts.createNewsCollection()
    except:
      pass
    return {"message": "Typesense: news collection created"}
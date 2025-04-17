import fetch_news
import fetch_utils
import generate_keywords
import fetch_earnings_calls
from model_client import ModelClient
from datastore_client import DatastoreClient
from auth_client import AuthClient
from typesense_client import TypesenseClient, CategoryNewsDocument

class Fetcher:
  def __init__(self):
    self.ds = DatastoreClient()
    self.ts = TypesenseClient()
    self.model = ModelClient()
    self.auth = AuthClient()
    
    self.initTypesenseServer()

  # Scrape Yahoo Finance news stories from the past 2 quarters
  def scrape_news(self, ticker: str):
    past_2_q = fetch_utils.get_past_8_quarters()[:1]

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
        text = '\n'.join(res["paragraphs"])
        # score using FinBERT model
        score_res = self.model.score_text(text)
        updated_doc = CategoryNewsDocument(ticker=ticker, score=score_res["score"], magnitude=score_res["magnitude"], **res)
        # Generate keywords for the story
        updated_doc.keywords = generate_keywords.generate_keywords_sorted(''.join(text))

        # Calculate scores for each paragraph
        paragraph_kws = []
        total_magnitude = 0
        weighted_sum = 0

        # Loop through paragraphs and calculate scores 
        for paragraph in res["paragraphs"]:
          if not paragraph:
            continue

          # Generate keywords for the paragraph
          p_keywords = generate_keywords.generate_keywords_sorted(paragraph)
          # Generate categorial score for the story
          # score using FinBERT model
          score_res = self.model.score_text(paragraph)
          if "error" in score_res:
            return {"messsage": f"ERROR {score_res['error']}"}

          sentiment_score = score_res["score"]
          magnitude = score_res["magnitude"]

          # Add to the total magnitude and weighted sum
          total_magnitude += magnitude
          weighted_sum += sentiment_score * magnitude
              
          # Append paragraph score details
          paragraph_kws.append({
            "score": sentiment_score,
            "magnitude": magnitude,
            "keywords": p_keywords
          })

        # Calculate the weighted average score
        if total_magnitude > 0:
            weighted_average_score = weighted_sum / total_magnitude
        else:
            weighted_average_score = 0

        updated_doc.score = weighted_average_score
        updated_doc.weighted_score = weighted_sum
        updated_doc.magnitude = total_magnitude
        updated_doc.paragraph_kws = paragraph_kws

        keywords = updated_doc.keywords
        for score_obj in paragraph_kws:
          for cat in score_obj["keywords"].keys():
            if cat not in keywords:
              existing_kw = score_obj["keywords"][cat]["keywords"]
              keywords[cat] = {"count": len(existing_kw), "keywords": existing_kw, "score": 0, "weighted_score": 0, "magnitude": 0}

            keywords[cat]["weighted_score"] += score_obj["score"] * score_obj["magnitude"]
            keywords[cat]["magnitude"] += score_obj["magnitude"]

        for cat in keywords.keys():
          if keywords[cat]["magnitude"] > 0:
            keywords[cat]["score"] = keywords[cat]["weighted_score"] / keywords[cat]["magnitude"]
          else:
            keywords[cat]["score"] = 0

        # save document to datastore
        self.ds.createNewsStoryEntity(updated_doc)
        
        # index into typesense
        try:
          self.ts.createNewsDocument(updated_doc)
          print("added: ", updated_doc.url)
        except Exception as e:
          print("failed: ", updated_doc.url, e)

        # aggregate scrape results
        results.append({"message": f"SUCCESS {updated_doc.url} score: {updated_doc.score} magnitude: {updated_doc.magnitude}"})

    return results
  
  def category_score_news(self, ticker: str):
      results = []
      urls = self.ds.getAllNewsDocIDs(ticker)
      
      for url in urls:
        res = self.category_score_news_by_url(url)
        results.append(res)

      return results

  def category_score_news_by_url(self, url: str):
    # Get text that we are scoring
    news_document = self.ds.getNewsDocByID(url)
    if not news_document or not hasattr(news_document, "paragraphs"):
      return {"message": "ERROR Invalid or missing news document"}
    
    if len(news_document.paragraphs) == len(news_document.paragraph_kws):
      return {"message": f"ERROR Document has already been scored"}
    
    updated_doc = CategoryNewsDocument(**(news_document.__dict__))
    # Generate keywords for the story
    updated_doc.keywords = generate_keywords.generate_keywords_sorted(''.join(news_document.paragraphs))

    # Calculate scores for each paragraph
    paragraph_kws = []
    total_magnitude = 0
    weighted_sum = 0

    # Loop through paragraphs and calculate scores 
    for paragraph in news_document.paragraphs:
      if len(paragraph) < 10: # disregard inputs less than 10 characters - irrelevant to sentiment
        continue

      # Generate keywords for the paragraph
      p_keywords = generate_keywords.generate_keywords_sorted(paragraph)
      # Generate categorial score for the story
      # score using FinBERT model
      score_res = self.model.score_text(paragraph)
      if "error" in score_res:
        return {"messsage": f"ERROR {score_res['error']}"}

      sentiment_score = score_res["score"]
      magnitude = score_res["magnitude"]

      # Add to the total magnitude and weighted sum
      total_magnitude += magnitude
      weighted_sum += sentiment_score * magnitude
          
      # Append paragraph score details
      paragraph_kws.append({
        "score": sentiment_score,
        "magnitude": magnitude,
        "keywords": p_keywords
      })

    # Calculate the weighted average score
    if total_magnitude > 0:
        weighted_average_score = weighted_sum / total_magnitude
    else:
        weighted_average_score = 0

    updated_doc.score = weighted_average_score
    updated_doc.weighted_score = weighted_sum
    updated_doc.magnitude = total_magnitude
    updated_doc.paragraph_kws = paragraph_kws

    keywords = updated_doc.keywords
    for score_obj in paragraph_kws:
      for cat in score_obj["keywords"].keys():
        if cat not in keywords:
          existing_kw = score_obj["keywords"][cat]["keywords"]
          keywords[cat] = {"count": len(existing_kw), "keywords": existing_kw, "score": 0, "weighted_score": 0, "magnitude": 0}

        keywords[cat]["weighted_score"] += score_obj["score"] * score_obj["magnitude"]
        keywords[cat]["magnitude"] += score_obj["magnitude"]

    for cat in keywords.keys():
      if keywords[cat]["magnitude"] > 0:
        keywords[cat]["score"] = keywords[cat]["weighted_score"] / keywords[cat]["magnitude"]
      else:
        keywords[cat]["score"] = 0

    # save document to datastore
    self.ds.createNewsStoryEntity(updated_doc)

    # Return the aggregated results
    return {"message": f"SUCCESS {updated_doc.url} score: {updated_doc.score} magnitude: {updated_doc.magnitude}"}
  

  def scrape_earnings_calls(self, ticker: str):
    past_8_q = fetch_utils.get_past_8_quarters()[2:]
    
    results = []
    for (y, q) in past_8_q:
      res = fetch_earnings_calls.fetch_earnings_call(ticker, y, q)
      if "error" in res:
        print(f"earnings call pull failed:", res['error'])
        results.append({"message": f"ERROR {res['error']}"})
        continue

      # score using FinBERT model
      score_res = self.model.score_text(res["transcript"])

      # add to datastore
      call = fetch_earnings_calls.EarningsCallTranscript(ticker=ticker, year=y, quarter=q, date=res["date"], paragraphs=res["transcript"].split('\n'), score=score_res["score"], magnitude=score_res["magnitude"])
      self.ds.createEarningsCallEntity(call)

      # index into typesense
      try:
        self.ts.createEarningsCallDocument(call)
        print("added: ", call.get_key())
      except Exception as e:
        print("failed: ", call.get_key(), e)

      results.append({"message": f"SUCCESS {call.get_key()}"})

    return results
  

  def backfillTypesenseServerNews(self, ticker: str):
    if ticker == "":
      print("resetting Typesense server")
      self.ts.deleteNewsCollection()
      self.ts.createNewsCollection()
    
    url_res = self.ts.getIndexedURLs(ticker)
    indexed_urls = set(url_res["urls"] if "urls" in url_res else [])
    ids = [id for id in self.ds.getAllNewsDocIDs(ticker) if id not in indexed_urls]
    
    fails = 0
    fail_msgs = []
    for id in ids:
      doc = self.ds.getNewsDocByID(id)
      try:
        self.ts.createNewsDocument(doc)
        print("added: ", doc.url)
      except Exception as e:
        print("failed: ", doc.url)
        fail_msgs.append(str(e))
        fails += 1

    return {"num_found": len(ids), "num_indexed": len(ids) - fails, "fail_msgs": fail_msgs}

  def backfillTypesenseServerEarningsCalls(self, ticker: str):
    raise Exception("not yet implemented")
    
  def initTypesenseServer(self):
    try:
      self.ts.createNewsCollection()
    except:
      pass

    try:
      self.ts.createEarningsCallCollection()
    except:
      pass
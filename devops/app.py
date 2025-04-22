from fetcher import Fetcher
from flask import Flask, jsonify, request

fetcher = Fetcher()
fetcher.initTypesenseServer()

app = Flask(__name__)

# Authorization middleware - passkey required on every request
@app.before_request
def before_request():
    token = request.headers.get("WBS-API-PASSKEY")
    print("GET THE TOKEN", token)
    if not token:
        token = request.cookies.get("WBS-API-PASSKEY")
        if not token:
            return jsonify({"message": "Passkey is missing."}), 403

    tokenRes = fetcher.auth.validate_passkey(token)
    if "valid" not in tokenRes or not tokenRes["valid"]:
        return jsonify({"message": tokenRes["error"]}), 403


# Test endpoint
@app.route('/')
def hello_world():
    return jsonify(message="Hello, World!")


@app.route('/category_score', methods=['GET'])
def category_score():
    # Get text that we are scoring
    # Take ticker to get the news stories or from URL
    # return categorial score for news story 
    # Use getNewsDocument to get our story
    # generate keywords for story
    # total magnitude of paragraphs for each category
    # sentiment score * magnitude of each category for weighted average bound by (-1,1)
    # add weighted average and magnitude, 

    # Getting URL parameter
    url = request.args.get("url", default="")
    if not url:
        return jsonify({"message": "missing required query param: url"}), 400
    

    
    # Get text that we are scoring
    news_document = fetcher.ds.getNewsDocByID(url)
    if not news_document or not hasattr(news_document, "paragraphs"):
        return jsonify({"message": "Invalid or missing news document"}), 404
    
    
    # Generate keywords for the story
    keywords = fetcher.generate_keywords_sorted(news_document)

    # Calculate scores for each paragraph
    paragraph_scores = []
    total_magnitude = 0
    weighted_sum = 0

    # Loop through paragraphs and calculate scores 
    for paragraph in news_document.paragraphs:
        # Generate categorial score for the story
        # score using FinBERT model
        score_res = fetcher.model.score_text('\n'.join(news_document.paragraphs))
        sentiment_score = score_res.get("sentiment_score", 0)
        magnitude = score_res.get("magnitude", 0)

        # Add to the total magnitude and weighted sum
        total_magnitude += magnitude
        weighted_sum += sentiment_score * magnitude
            
        # Append paragraph score details
        paragraph_scores.append({
            "paragraph": paragraph,
            "sentiment_score": sentiment_score,
            "magnitude": magnitude
        })

        # Calculate the weighted average score
        if total_magnitude > 0:
            weighted_average_score = weighted_sum / total_magnitude
        else:
            weighted_average_score = 0

        # Return the aggregated results
        return jsonify({
            "weighted_average_score": round(weighted_average_score, 2),
            "total_magnitude": round(total_magnitude, 2),
            "paragraph_scores": paragraph_scores,
            "keywords": keywords
        })    
    

# Scrape news using Selenium and requests, stores in Datastore
@app.route('/scrape_news', methods=['GET'])
def scrape_news():
    ticker = request.args.get("ticker", default="")
    if ticker == "":
        return jsonify({"message": "missing required query param: ticker"}), 400
    
    res = fetcher.scrape_news(ticker)
    return jsonify({"num_attempts": len(res), "num_success": len([r for r in res if "error" not in r]), "results": res})


# Full text search on news articles using ticker and search term
@app.route('/search_news', methods=['GET'])
def search_news():
    ticker = request.args.get("ticker", default="")
    if ticker == "":
        return jsonify({"message": "missing required query param: ticker"}), 400
    
    search_term = request.args.get("search_term", default="")

    res = fetcher.ts.searchNews(ticker, search_term)
    return jsonify(res)


# Get tickers indexed in typesense
@app.route('/search_news/indexed_tickers', methods=['GET'])
def indexed_tickers():
    res = fetcher.ts.getIndexedTickers()
    return jsonify(res)


# Get all news article scores for a ticker
@app.route('/search_news/summary', methods=['GET'])
def summarize():
    ticker = request.args.get("ticker", default="")
    if ticker == "":
        return jsonify({"message": "missing required query param: ticker"}), 400
    
    res = fetcher.ts.getScoresByTicker(ticker)
    return jsonify(res)


# Score the news stories in Datastore for a ticker, save scores to Datastore
@app.route('/score_news', methods=['GET'])
def score_news():
    ticker = request.args.get("ticker", default="")
    if ticker == "":
        return jsonify({"message": "missing required query param: ticker"}), 400
    
    res = fetcher.score_news(ticker)
    return jsonify({"num_attempts": len(res), "num_success": len([r for r in res if "error" not in r]), "results": res})


# Backfill Typesense server with Datastore content
@app.route('/backfill_typesense', methods=['GET'])
def backfill():
    ticker = request.args.get("ticker")
    
    res = fetcher.backfillTypesenseServer(ticker)
    return jsonify(res)




if __name__ == "__main__":
    app.run(debug=True)

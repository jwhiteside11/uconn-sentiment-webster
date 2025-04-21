import requests
import matplotlib.pyplot as plt
import datetime
from collections import defaultdict

# Define stock tickers
tickers = ["WBS", "ZION", "MTB", "VLY", "CFR"]

# API endpoint
AUTH_URL = "http://34.44.103.189:5100/auth/authenticate"
API_URL = "http://34.44.103.189:5100/api/search_news/summary?ticker={}"

# creds
USERNAME = "testuser"
PASSWORD = "password123"

def get_passkey():
    # set payload and headers
    payload = {"username": USERNAME, "password": PASSWORD}
    headers = {"Content-Type": "application/json"}

    # call url to get passkey
    response = requests.post(AUTH_URL, json=payload, headers=headers)

    if response.status_code == 200:
        login_data = response.json()
        if "passkey" in login_data:
            return login_data["passkey"]
        else:
            print("Authentication failed: No passkey returned.")
    else:
        print(f"Authentication failed: {response.status_code} - {response.text}")
    return None

PASSKEY = get_passkey()
if not PASSKEY:
    exit("Failed to authenticate. Check username and password.")

def fetch_sentiment_data(ticker):
    # call url to get sentiment data
    cookies = {"WBS-API-PASSKEY": PASSKEY}
    response = requests.get(API_URL.format(ticker), cookies=cookies)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data for {ticker}: {response.status_code}")
        return None
    
def parse_sentiment_data(ticker):
    # fetch sentiment data and store json obj in result
    result = fetch_sentiment_data(ticker) 

    # create a dictionary to store monthly scores
    monthly_scores = defaultdict(list)

    if result and isinstance(result.get("documents"), list):
        for doc in result["documents"]:
            try:
                date = datetime.datetime.strptime(doc["date"], "%a, %b %d, %Y, %I:%M %p")
                month = date.strftime("%Y-%m")  # e.g., '2025-01'
                monthly_scores[month].append(doc["score"])
            except Exception as e:
                print(f"Error parsing date for {ticker}: {doc['date']} - {e}")

    # calculate average sentiment score for each month
    return {month: sum(scores) / len(scores) for month, scores in monthly_scores.items()}

# collect and process data for each ticker
data = {ticker: parse_sentiment_data(ticker) for ticker in tickers}

# plot the data
plt.figure(figsize=(12, 6))
for ticker, monthly_data in data.items():
    if not monthly_data:
        continue  # skip tickers with no data

    months, avg_scores = zip(*sorted(monthly_data.items()))
    plt.plot(months, avg_scores, marker="o", linestyle="-", label=ticker)

# plot formatting
plt.xlabel("Date (Months & Year)")
plt.ylabel("Average Sentiment Score (-1 to 1)")
plt.title("Average Monthly Sentiment Scores for Different Tickers")
plt.axhline(0, color="black", linewidth=0.5, linestyle="--")
plt.ylim(-1, 1)
plt.legend()
plt.xticks(rotation=45)
plt.grid()

plt.show()

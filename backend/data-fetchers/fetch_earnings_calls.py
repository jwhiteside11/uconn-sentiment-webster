import requests
from typing import List, Union
import os
import json

class EarningsCallTranscript:
    def __init__(self, ticker: str, year: int, quarter: int, date: str, paragraphs: list[str], score: float = 0, magnitude: float = 0, id: str = ""):
        self.ticker = ticker
        self.year = year
        self.quarter = quarter
        self.date = date
        self.paragraphs = paragraphs
        self.score = score
        self.magnitude = magnitude

    def get_key(self):
      return f'call-{self.ticker}-Y{self.year}-Q{self.quarter}'

APININJAS_API_KEY = os.getenv('APININJAS_API_KEY', "")

def get_authenticated(url):
  # use headers for API key
  headers = {'X-Api-Key': APININJAS_API_KEY}
  return requests.get(url, headers=headers)

# Fetch a specified earning calls from API Ninjas (requires API key)
def fetch_earnings_call(ticker: str, year: int, quarter: int) -> Union[List[str], dict]:
  res = get_authenticated(f"https://api.api-ninjas.com/v1/earningstranscript?ticker={ticker}&year={year}&quarter={quarter}")
  if res.status_code != 200:
    return {"error": f"{res.status_code}: {res.text}", "ticker": ticker, "year": year, "quarter": quarter}
  
  try:
    resObj = json.loads(res.text)  
  except Exception as e:
    return {"error": f"{e}", "ticker": ticker, "year": year, "quarter": quarter}
  
  if type(resObj) != dict:
    return {"error": "earnings call not available", "ticker": ticker, "year": year, "quarter": quarter}
 
  return resObj

# driver for running in production
def run_program():
  pass

# driver for testing different functions
def test_program():
  pass


# main driver
if __name__ == "__main__":
  test_program()
  # run_program()
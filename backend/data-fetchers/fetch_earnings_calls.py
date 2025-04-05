import subprocess
import requests
from typing import List, Union
import pandas as pd
import time
import os
import json

import fetch_utils

class EarningsCallTranscript:
    def __init__(self, ticker: str, year: int, quarter: int, date: str, paragraphs: list[str], score: float = 0, magnitude: float = 0, id: str = ""):
        self.ticker = ticker
        self.year = year
        self.quarter = quarter
        self.date = date
        self.paragraphs = paragraphs
        self.score = score
        self.magnitude = magnitude

APININJAS_API_KEY = os.getenv('APININJAS_API_KEY', "")

def get_authenticated(url):
  # use headers for API key
  headers = {'X-Api-Key': APININJAS_API_KEY}
  return requests.get(url, headers=headers)

'''
Fetch a specified earning calls from API Ninjas (requires API key)

Output: paragraphs from the specified earnings call
Example usage:
  p_res = earnings_calls("MSFT", year=2025, quarter=1)
'''
def fetch_earnings_call(ticker: str, year: int, quarter: int) -> Union[List[str], dict]:
  res = get_authenticated(f"https://api.api-ninjas.com/v1/earningstranscript?ticker={ticker}&year={year}&quarter={quarter}")
  if res.status_code != 200:
    return {"error": f"{res.status_code}: source.text", "ticker": ticker, "year": year, "quarter": quarter}
  
  try:
    resObj = json.loads(res.text)  
  except Exception as e:
    return {"error": f"{e}", "ticker": ticker, "year": year, "quarter": quarter}
  
  if type(resObj) != dict:
    return {"error": "earnings call not available", "ticker": ticker, "year": year, "quarter": quarter}
 
  return {
    "ticker": ticker, 
    "year": year, 
    "quarter": quarter,
    
  }

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
import subprocess
import requests
from typing import List
import pandas as pd
import time
import os
import json

import fetch_utils


def get_authenticated(url):
  # use headers for API key
  headers = {'X-Api-Key': os.getenv('APININJAS_API_KEY')}
  return requests.get(url, headers=headers)


'''
Fetch a specified earning calls from API Ninjas (requires API key)

Output: paragraphs from the specified earnings call
Example usage:
  p_res = earnings_calls("MSFT", year=2025, quarter=1)
'''
def earnings_calls(ticker: str, year: int, quarter: int) -> List[str]:
  source = get_authenticated(f"https://api.api-ninjas.com/v1/earningstranscript?ticker={ticker}&year={year}&quarter={quarter}")
  if source.status_code != 200:
    print("Error:", source.status_code, source.text)
    return []
  
  try:
    resObj = json.loads(source.text)
    paragraphs = resObj['transcript'].split('\n')
  except:
    print("Failed to decode JSON response.", ticker, f"{year}Q{quarter}")
    return []

  return paragraphs


'''
Scrape earning calls for the past 8 quarters for the specified ticker

Output: saves list of paragraphs as csv
Example usage:
  earnings_dict = save_earnings_calls("MSFT")
'''
def save_earnings_calls(ticker: str):
  past8Q = fetch_utils.get_past_8_quarters()
  
  [firstY, firstQ] = past8Q[-1]
  [lastY, lastQ] = past8Q[0]
  file_path = f'earnings-call-{ticker}-{firstY}Q{firstQ}-{lastY}Q{lastQ}.xlsx'

  dfs = []
  for (year, quarter) in past8Q:
    res = earnings_calls(ticker, year, quarter)
    dfs.append(pd.DataFrame({f"{year} Q{quarter}" : res}))
    # sleep to avoid rate limiting
    time.sleep(2)

  df = pd.concat(dfs, axis=1, join='outer')
  # write dataframe to local file
  df.to_excel(file_path)

  # copy local file to google cloud
  subprocess.run(["gcloud", "storage", "cp", f"{file_path}", "gs://earnings-calls-raw/"])

  # remove local file
  os.remove(file_path)



# driver for running in production
def run_program():
  save_earnings_calls("INTU")

# driver for testing different functions
def test_program():
  p = earnings_calls("MSFT", 2024, 3)
  print(p)


# main driver
if __name__ == "__main__":
  test_program()
  # run_program()
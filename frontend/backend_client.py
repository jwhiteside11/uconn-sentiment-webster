import requests
import os

class BackendClient:
  def __init__(self):
    API_URL: str = os.getenv("WBS_API_URL", "http://reverse_proxy:5100")
    self.PUBLIC_API_URL: str = f'{API_URL}/api'
    self.PUBLIC_AUTH_URL: str = f'{API_URL}/auth'

  def AUTH_POST(self, path: str, data: dict):
    return requests.post(self.PUBLIC_AUTH_URL + path, json=data)
  
  def API_GET(self, path: str, passkey: str):
    return requests.get(self.PUBLIC_API_URL + path, headers={"WBS-API-PASSKEY": passkey})
  
  def login(self, username: str, password: str):
    return self.AUTH_POST(f'/authenticate', {"username": username, "password": password})

  def validate(self, passkey: str):
    return self.AUTH_POST(f'/validate', {"passkey": passkey})
  
  def search_news(self, ticker: str, search_term: str, passkey: str):
    return self.API_GET(f'/search_news?ticker={ticker}&search_term={search_term}', passkey)
  
  def get_tickers(self, passkey: str):
    return self.API_GET('/search_news/indexed_tickers', passkey)
  
  def get_summary(self, ticker: str, passkey: str):
    return self.API_GET(f'/search_news/summary?ticker={ticker}', passkey)
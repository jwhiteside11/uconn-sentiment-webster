import requests
import json

class ModelClient:
    def __init__(self):
        self.model_url = 'http://host.docker.internal:5400'
    
    def score_text(self, text: str):
        try:
            res = requests.post(f'{self.model_url}/score_text', json={"text_content": text}).json()
            return res
        except Exception as e:
            return {"error": f"{e}"}


def run_program():
    pass
    
def test_program():
    pass

if __name__ == "__main__":
    run_program()
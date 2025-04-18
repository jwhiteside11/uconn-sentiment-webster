import requests
import json

class AuthClient:
    def __init__(self):
        self.auth_url = 'http://auth_server:5200'
    
    def validate_passkey(self, passkey: str):
        try:
            res = requests.post(f'{self.auth_url}/validate', json={"passkey": passkey})
            if res.status_code != 200:
                return {"error": f"ERROR {res.text}"}
            return res.json()
        except Exception as e:
            return {"error": f"ERROR {e}"}


def run_program():
    pass
    
def test_program():
    pass

if __name__ == "__main__":
    run_program()
import requests
import json

class AuthClient:
    def __init__(self):
        self.auth_url = 'http://host.docker.internal:5200'
    
    def validate_passkey(self, passkey: str):
        try:
            res = requests.post(f'{self.auth_url}/validate', json={"passkey": passkey}).json()
            return res
        except Exception as e:
            return {"message": f"ERROR {e}"}


def run_program():
    pass
    
def test_program():
    pass

if __name__ == "__main__":
    run_program()
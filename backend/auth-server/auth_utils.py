import bcrypt
import jwt
import os
import datetime

class Authenticator:
    def __init__(self):
        self.SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
        # Mock user storage
        self.users = {
            "testuser": bcrypt.hashpw("password123".encode(), bcrypt.gensalt())
        }


    def authenticate(self, username, password):
        if not username or not password:
            return {"error": "Username and password are required"}
        
        try:
            if username in self.users and bcrypt.checkpw(password.encode(), self.users[username]):
                exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
                token = jwt.encode({"username": username, "exp": exp_time}, self.SECRET_KEY, algorithm="HS256")
                return {"passkey": token}
            
            return {"error": "Invalid credentials"}
        except Exception:
            return {"error": "Failed to encode token"}


    def validate(self, passkey):
        if not passkey:
            return {"error": "Passkey is required"}
        
        try:
            decoded = jwt.decode(passkey, self.SECRET_KEY, algorithms=["HS256"])
            return {"valid": True, "username": decoded["username"]}
        except jwt.ExpiredSignatureError:
            return {"error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}
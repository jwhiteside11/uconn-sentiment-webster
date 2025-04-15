from flask import Flask, request, jsonify
from flask_cors import CORS
from auth_utils import Authenticator

auth = Authenticator()

app = Flask(__name__)
CORS(app)

@app.route("/authenticate", methods=["POST"])
def authenticate():
    data = request.json
    username = data.get("username")
    password = data.get("password").encode()
    
    res = auth.authenticate(username, password)

    if "error" in res:
        return jsonify(res), 401
    
    return jsonify(res), 200


@app.route("/validate", methods=["POST"])
def validate():
    data = request.json
    token = data.get("passkey")

    res = auth.validate(token)

    if "error" in res:
        return jsonify(res), 401
    
    return jsonify(res), 200


if __name__ == "__main__":
    app.run(debug=True)  
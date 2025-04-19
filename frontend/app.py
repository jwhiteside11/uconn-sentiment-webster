from backend_client import BackendClient
from flask import Flask, jsonify, render_template, request, make_response, redirect, url_for
import functools

api_client = BackendClient()

app = Flask(__name__)

# Middleware for authentication
def passkey_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        passkey = request.cookies.get('WBS-API-PASSKEY')
        if not passkey:
            return jsonify({"message": "Passkey is missing."}), 403

        passkeyRes = api_client.validate(passkey).json()
        if "valid" not in passkeyRes or not passkeyRes["valid"]:
            return jsonify({"message": passkeyRes["error"]}), 403

        return f(*args, **kwargs)

    return decorated_function

# Base URL - redirect users to login page
@app.route('/')
def base():
    return redirect(url_for('login_get'))

# Login page - renders login form
@app.route('/login', methods=['GET'])
def login_get():
    return render_template("login.html")

# Login handler - receives JSON credentials
@app.route('/login', methods=['POST'])
def login_post():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username and password:
        loginRes = api_client.login(username, password).json()
        if "passkey" in loginRes:
            response = jsonify({"success": True})
            response.set_cookie('WBS-API-PASSKEY', loginRes["passkey"], max_age=3600, samesite=None)
            return response

    return jsonify({"success": False, "error": "Invalid login"}), 401

# Search news using Typesense
@app.route('/search_news', methods=['GET'])
@passkey_required
def search_news():
    passkey = request.cookies.get('WBS-API-PASSKEY')
    res = api_client.get_tickers(passkey).json()
    return render_template("search_news.html", ticker_list=res["tickers"], api_url=api_client.PUBLIC_API_URL)

# Data visualization graphs
@app.route('/graph_news', methods=['GET'])
@passkey_required
def graph():
    passkey = request.cookies.get('WBS-API-PASSKEY')
    ticker_res = api_client.get_tickers(passkey).json()
    summary_res = api_client.get_summary("WBS", passkey).json()
    return render_template("graphs_example.html", ticker_list=ticker_res["tickers"], summary=summary_res)

if __name__ == "__main__":
    app.run(debug=True)

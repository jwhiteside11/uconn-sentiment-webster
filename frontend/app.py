from backend_client import BackendClient
from flask import Flask, jsonify, render_template, request, make_response, redirect, url_for, flash
import functools

api_client = BackendClient()

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Base URL - redirect users to login page
@app.route('/')
def base():
    return redirect(url_for('login_get'))

# Login page - renders login form
@app.route('/login', methods=['GET'])
def login_get():
    return render_template("login.html")

# Login handler - receives HTML form credentials
@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get("username")
    password = request.form.get("password")

    if username and password:
        loginRes = api_client.login(username, password).json()
        if "passkey" in loginRes:
            response = make_response(redirect(url_for("graph_news")))
            response.set_cookie('WBS-API-PASSKEY', loginRes["passkey"], max_age=3600, samesite=None) # set passkey to cookie that lasts 1 hour
            return response
        else:
            flash(loginRes)
    else:
        flash("Username and passowrd required.")

    return render_template("login.html")

# Authenticated routes

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

# Search news using Typesense
@app.route('/search_news', methods=['GET'])
@passkey_required
def search_news():
    passkey = request.cookies.get('WBS-API-PASSKEY')
    try:
        res = api_client.get_tickers(passkey).json()
    except Exception as e:
        print(e)
        return make_response(redirect(url_for("login")))
    
    return render_template("search_news.html", ticker_list=res["tickers"], api_url=api_client.PUBLIC_API_URL)

# Data visualization graphs
@app.route('/graph_news', methods=['GET'])
@passkey_required
def graph_news():
    passkey = request.cookies.get('WBS-API-PASSKEY')
    try:
        ticker_res = api_client.get_tickers(passkey).json()
        summary_res = api_client.get_summary("WBS", passkey).json()
    except Exception as e:
        print(e)
        return make_response(redirect(url_for("login")))
    
    return render_template("graphs_example.html", ticker_list=ticker_res["tickers"], summary=summary_res, api_url=api_client.PUBLIC_API_URL)


if __name__ == "__main__":
    app.run(debug=True)

import os
import requests
import sqlite3
from flask import Flask, flash, redirect, render_template, url_for, request, session
from flask_session import Session
from dotenv import load_dotenv
from helpers import apology, login_required
from google.oauth2 import id_token
from google.auth.transport import requests as grequests


load_dotenv()
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

connection = sqlite3.connect("gencord.db")
cursor = connection.cursor()

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
 

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    return render_template("index.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"response_type=code&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&scope=openid email profile"
    )
    return redirect(google_auth_url)
    

@app.route("/search")
def servers():
    return render_template("search.html")


@app.route("/callback")
def callback():
    code = request.args.get("code")
    
    # Exchange code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    token_response = requests.post(token_url, data=token_data).json()
    
    id_token_jwt = token_response["id_token"]

    try:
        idinfo = id_token.verify_oauth2_token(id_token_jwt, grequests.Request(), GOOGLE_CLIENT_ID)

        session["user"] = {
            "id": idinfo["sub"],
            "email": idinfo["email"],
            "name": idinfo["name"],
            "picture": idinfo["picture"]
        }
    except ValueError:
        return "Invalid token", 400
    
    return redirect("/search")

def exchange_code(code, redirect_uri):
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post(
        'https://discord.com/api/v10/oauth2/token',
        data=data,
        headers=headers,
        auth=(MY_CLIENT_ID, MY_CLIENT_SECRET)
    )

    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        apology("HTTP error occurred", 400)
    except requests.exceptions.RequestException as e:
        apology("A request error occurred", 400)

    return r.json()



def getorpost_info(path, method, json=None, access_token=None, bot=False):
    """
    Get or post information to the specified API path. Set bot=True to use a bot token.

    :param path: Full URL for the API endpoint.
    :type path: str
    :param method: HTTP method — 0 for GET, 1 for POST.
    :type method: int
    :param json: Optional JSON data for POST requests.
    :type json: dict or None
    :param access_token: User access token for authorization (ignored if bot=True).
    :type access_token: str
    :param bot: Set to True to use bot token from MY_TOKEN.
    :type bot: bool
    :raises: Returns apology message on HTTP or network error.
    :return: JSON response from the API.
    :rtype: dict
    """

    
    auth_header = f"Bot {MY_TOKEN}" if bot else f"Bearer {access_token}"
    headers = {'Authorization': auth_header}
    
    if method == 1:
        headers["Content-Type"] = "application/json"

    try:
        if method == 0:
            r = requests.get(path, headers=headers)
        else:
            r = requests.post(path, headers=headers, json=json)
        r.raise_for_status()
        return r.json()
    
    except Exception as e:
        status_code = r.status_code if "r" in locals() else 500
        return apology(f"Oh there is a problem: {e}", status_code)


@app.errorhandler(404)
def page_not_found(e):
    return apology("Looks like page not found", 404)


@app.errorhandler(500)
def page_not_found(e):
    return apology("Internal Server Error", 500)


if __name__ == '__main__': 
    app.run()
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


@app.route("/logout")
def logout():
    session.clear()

    return redirect("/")
    

@app.route("/search")
def servers():
    return render_template("search.html")


@app.route("/callback")
def callback():
    code = request.args.get("code")
    
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


@app.errorhandler(404)
def page_not_found(e):
    return apology("Looks like page not found", 404)


@app.errorhandler(500)
def page_not_found(e):
    return apology("Internal Server Error", 500)


if __name__ == '__main__': 
    app.run()
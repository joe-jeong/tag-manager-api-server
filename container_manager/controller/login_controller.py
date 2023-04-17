import json
import os
from container_manager import login_manager, client
from container_manager.models import User

from flask import Blueprint, redirect, request, url_for
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)
from oauthlib.oauth2 import WebApplicationClient
import requests
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_DISCOVERY_URL

bp = Blueprint('login', __name__, url_prefix='/')
google_provider_conf = requests.get(GOOGLE_DISCOVERY_URL).json()


@bp.route("/")
def index():
    if current_user.is_authenticated:
        return (
            "<p>Hello, {}! You're logged in! Email: {}</p>"
            "<div><p>Google Profile Picture:</p>"
            '<img src="{}" alt="Google profile pic"></img></div>'
            '<a class="button" href="/logout">Logout</a>'.format(
                current_user.name, current_user.email, current_user.profile_pic
            )
        )
    else:
        return '<a class="button" href="/login/google">Google Login</a>'


@bp.route('/login/google')
def login():
    authorization_endpoint = google_provider_conf["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"]
    )
    return redirect(request_uri)


@bp.route("/login/google/callback")
def google_callback():
    code = request.args.get("code")
    token_endpoint = google_provider_conf['token_endpoint']

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code = code
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
    )

    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_conf['userinfo_endpoint']
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        user_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google", 400

    user = User(email=email, nickname=user_name)

    if not User.get_by_email(email):
        User.create(email, user_name)
    
    login_user(user)

    return redirect(url_for("index"))


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
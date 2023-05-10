import json
from app import client, jwt, redis
from app.model.user import User
from app.model.oauth_service import OauthService
from datetime import timedelta, time

from flask import Blueprint, redirect, request, url_for, jsonify, make_response
from flask_restx import Namespace, Resource, fields

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_jwt
)
import requests
from app.config.flask_config import DevConfig

bp = Blueprint('login', __name__, url_prefix='/')
ns = Namespace(
    'auth',
    '인증 관련 API'
    )
google_provider_conf = requests.get(DevConfig.GOOGLE_DISCOVERY_URL).json()


@bp.route("/home")
def index():
    return '<a class="button" href="/login/google">Google Login</a>'


@bp.route('/login/google')
def login():
    authorization_endpoint = google_provider_conf["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"]
    )

    # return jsonify({"redirect_uri":request_uri}), 200
    return redirect(request_uri)


@bp.route("/login/google/callback")
def google_callback():
    code = request.args.get("code")
    token_endpoint = google_provider_conf['token_endpoint']

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        # redirect_url="http://localhost:3000/login/google/callbacks"
        redirect_url=request.base_url,
        code = code
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(DevConfig.GOOGLE_CLIENT_ID, DevConfig.GOOGLE_CLIENT_SECRET)
    )

    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_conf['userinfo_endpoint']
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        user_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google", 400

    oauth_id = OauthService.get_by_name('google').id
    user = User.get_by_oauth_asset_id(oauth_id, unique_id)

    if not user:
        User.save(oauth_id, unique_id)
        user = User.get_by_oauth_asset_id(oauth_id, unique_id)

    access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=3))
    refresh_token = create_refresh_token(identity=user.id)
    redis.set(refresh_token, user.id, ex=timedelta(days=7))

    return jsonify({'username': user_name, 'access_token': access_token, 'refresh_token': refresh_token}), 200


@bp.route('/reissue', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    old_refresh_token = request.headers.get('Authorization').replace('Bearer ', '')
    redis_user_id = int(redis.get(old_refresh_token))

    if redis_user_id != current_user_id:
        return jsonify({'msg': 'Invalid token'}), 401
    
    access_token = create_access_token(identity=current_user_id, expires_delta=timedelta(hours=1))
    refresh_token = create_refresh_token(identity=current_user_id)
    redis.delete(old_refresh_token)
    redis.set(refresh_token, current_user_id, ex=timedelta(days=7))
    return jsonify(access_token=access_token, refresh_token=refresh_token)


# TODO 로그아웃 시 기존 access token 블랙리스트 추가
@bp.route("/logout")
@jwt_required()
def logout():
    access_token, refresh_token = request.headers.get('Authorization').replace('Bearer ', '').split()
    
    redis.delete(refresh_token)
    jti = get_jwt()['jti']
    redis.set(jti, 'true', ex=get_jwt()['exp'] - time())
    return jsonify({"msg": "Logout successful"}), 200
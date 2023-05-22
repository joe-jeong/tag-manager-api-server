import json
from app import client, jwt, redis
from app.model.user import User
from app.model.oauth_service import OauthService
from datetime import timedelta, time
from urllib.parse import urlencode
from flask import Blueprint, redirect, request, url_for, jsonify, make_response
from flask_restx import Namespace, Resource, fields, reqparse

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_jwt
)
import requests
from app.config.flask_config import DevConfig
from app.utils.auth_util import generate_user_code

bp = Blueprint('login', __name__, url_prefix='/')
ns = Namespace(
    name='auth',
    description='인증 관련 API',
    path='/'
)

google_provider_conf = requests.get(DevConfig.GOOGLE_DISCOVERY_URL).json()

class _Schema():
    reissue_fields = ns.model('reissue 요청 반환 정보', {
        'access_token': fields.String(description='access token 값', example='eyJhbGciOiJIUzI1NiIsI...'),
        'refresh_token': fields.String(description='refresh token 값', example='eyJhbGciOiJIUzI1NiIsI...'),
        'code': fields.String(description='user code', example='A1B2C3D4')
    })

    login_result_fields = ns.inherit('로그인 후 토큰 반환 정보', reissue_fields, {
        'code': fields.String(description='user code', example='A1B2C3D4')
    })

    msg_fields = ns.model('상태 코드에 따른 설명', {
        'msg': fields.String(description='상태 코드에 대한 메세지', example='처리 내용')
    })


@bp.route("/home")
def login_button_page():
    """로그인 테스트를 위한 로그인 버튼 페이지"""
    return '<a class="button" href="/login/google/test">Google Login</a>'


@bp.route('/login/google/test')
def redirect_google_page():
    """로그인 테스트를 위한 구글 로그인 페이지 리다이렉트"""
    authorization_endpoint = google_provider_conf["authorization_endpoint"]
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.root_url + "login/google",
        scope=["openid", "email", "profile"]
    )
    return redirect(request_uri)


@ns.route("/login/google")
@ns.doc(params={'code': {'description': '구글 oauth 서버에서 받은 secret code', 'in': 'query', 'type': 'string'},})
class GoogleLogin(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('code', type=str, help="구글 코드")

    @ns.response(200, '회원가입/로그인 성공', _Schema.login_result_fields)
    def get(self):
        """구글 인증코드를 사용한 로그인 처리"""
        args = self.parser.parse_args()
        code = args['code']
        token_endpoint = google_provider_conf['token_endpoint']
        token_request_payload = {
                'code': code,
                'client_id': DevConfig.GOOGLE_CLIENT_ID,
                "client_secret": DevConfig.GOOGLE_CLIENT_SECRET,
                'redirect_uri': 'http://localhost:3000/login/google/callback',
                #'redirect_uri': request.base_url,

                'grant_type': 'authorization_code'
            }

        token_response = requests.post(
            token_endpoint,
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data=token_request_payload
        )
        token_body = token_response.json()
        access_token = token_body['access_token']
        # client.parse_request_body_response(json.dumps(token_response.json()))

        userinfo_endpoint = google_provider_conf['userinfo_endpoint']
        # uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(
            userinfo_endpoint,
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                },
            )

        if userinfo_response.json().get("email_verified"):
            unique_id = userinfo_response.json()["sub"]
            user_name = userinfo_response.json()["given_name"]
        else:
            return "User email not available or not verified by Google", 400

        oauth = OauthService.get_by_name('google')
        user = User.get_by_oauth_asset_id(oauth, unique_id)

        if not user:
            code = generate_user_code()
            User.save(oauth.id, unique_id, code)
            user = User.get_by_oauth_asset_id(oauth, unique_id)

        access_token = create_access_token(identity=user.code, expires_delta=timedelta(hours=10))
        refresh_token = create_refresh_token(identity=user.code)
        redis.set(refresh_token, user.id, ex=timedelta(days=7))

        return {'user_code': user.code, 'access_token': access_token, 'refresh_token': refresh_token}, 200


@jwt_required(refresh=True)
@ns.route('/reissue')
class Refresh(Resource):

    @ns.response(200, 'reissue 성공', _Schema.reissue_fields)
    def post(self):
        """reissue 요청"""
        current_user_id = get_jwt_identity()
        old_refresh_token = request.headers.get('Authorization').replace('Bearer ', '')
        redis_user_id = int(redis.get(old_refresh_token))

        if redis_user_id != current_user_id:
            return jsonify({'msg': 'Invalid token'}), 401
        
        access_token = create_access_token(identity=current_user_id, expires_delta=timedelta(hours=1))
        refresh_token = create_refresh_token(identity=current_user_id)
        redis.delete(old_refresh_token)
        redis.set(refresh_token, current_user_id, ex=timedelta(days=7))
        return {"access_token": access_token, "refresh_token": refresh_token}


# TODO 로그아웃 시 기존 access token 블랙리스트 추가
@jwt_required()
@ns.route("/logout")
class Logout(Resource):
    def post(self):
        """로그아웃 요청"""
        access_token, refresh_token = request.headers.get('Authorization').replace('Bearer ', '').split()
        
        redis.delete(refresh_token)
        jti = get_jwt()['jti']
        redis.set(jti, 'true', ex=get_jwt()['exp'] - time())
        return {"msg": "Logout successful"}, 200
    
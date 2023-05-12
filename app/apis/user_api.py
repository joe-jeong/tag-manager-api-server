from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import json

from app.model.medium import Medium, PlatformList
from app.model.tag import Tag
from flask_restx import Namespace, Resource, fields, reqparse

ns = Namespace(
    name='user',
    description='유저 관련 API'
)

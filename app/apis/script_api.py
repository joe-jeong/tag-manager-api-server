from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pathlib import Path
import os

from app.model.medium import Medium, PlatformList
from app.model.container import Container
from app.model.script import Script
from flask_restx import Namespace, Resource, fields, reqparse
from app.utils import s3_util, script_util

ns = Namespace(name='script', description='스크립트 관련 API', path='/')

current_file_path = Path(__file__).resolve()
js_files_dir_path = current_file_path.parents[2] / 'js_files'

@ns.route('/scripts/<string:container_domain>')
class ScriptManager(Resource):

    def get(self, container_domain):
        container = Container.get_by_domain(container_domain)
        script = Script.get_recent_script(container)
        return {'s3_path':script.s3_path}, 200


    def post(self, container_domain):
        container = Container.get_by_domain(container_domain)
        script_util.make_file(container)
        filename, s3_path = s3_util.put_js_on_s3(js_files_dir_path / 'script.js')
        Script.save(filename, s3_path, container)

        return {"msg": 'ok'}, 201
        

        

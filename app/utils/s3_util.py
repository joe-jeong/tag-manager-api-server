import boto3
import os
import uuid
import re
from flask_jwt_extended import get_jwt_identity

from app.config.container_config import AWS_ACCESS_KEY, AWS_SECRET_KEY, BUCKET_NAME
from app.model.container import Container
from app.utils import container_util

s3_base_url = f"https://{BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com/"

def s3_connection():
    return boto3.client('s3',
                      aws_access_key_id = AWS_ACCESS_KEY,
                      aws_secret_access_key = AWS_SECRET_KEY
                      )


def s3_resource():
    return boto3.resource('s3',
                      aws_access_key_id = AWS_ACCESS_KEY,
                      aws_secret_access_key = AWS_SECRET_KEY
                      )


def extract_path_from_url(url):
    pattern = r'https?://[^/]+/(.*)'
    match = re.match(pattern, url)
    return match.group(1) if match else None


def put_s3(code:str, folder_name:str):
    filename = str(uuid.uuid4()) + '.js'

    s3_client = s3_connection()
    s3_path = f"{folder_name}/{filename}"
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_path,
        Body = bytes(code, encoding='utf8'),
        ContentType='text/plain',
        ContentEncoding='utf-8'

    )    
    s3_url = f"https://{BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com/{s3_path}"

    return s3_path, s3_url

def delete_s3(key:str):
    s3_client = s3_connection()
    s3_client.delete_object(Bucket=BUCKET_NAME, Key=key)

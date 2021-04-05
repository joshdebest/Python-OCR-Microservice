import boto3
import botocore
import json
import logging

session = boto3.Session(profile_name="default")

endpoint_url = ''


def set_bucket_policy(bucket_name):
    # TODO Update bucket policy for production
    bucket_policy = {
        'Version': '2012-10-17',
        'Statement': [{
            'Sid': 'PublicRead',
            'Effect': 'Allow',
            'Principal': '*',
            'Action': ['s3:GetObject', "s3:GetObjectVersion"],
            'Resource': ['arn:aws:s3:::{bucket_name}/*']
        }]
    }
    # Convert the policy from JSON dict to string
    bucket_policy = json.dumps(bucket_policy)
    # Set the new policy
    s3 = session.client('s3', endpoint_url=endpoint_url)
    response = s3.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)
    print("set_bucket_policy response:\n", response)

def get_bucket_policy(bucket_name):
    try:
        s3 = session.client('s3', endpoint_url=endpoint_url)
        response = s3.get_bucket_policy(Bucket=bucket_name)
        print("get_bucket_policy response:\n", response)

    except botocore.exceptions.ClientError as err:
        status = err.response["ResponseMetadata"]["HTTPStatusCode"]
        errcode = err.response["Error"]["Code"]
        if status == 404:
            logging.warning("Missing object, %s", errcode)
        elif status == 403:
            logging.error("Access denied, %s", errcode)
        else:
            logging.exception("Error in request, %s", errcode)
    return {}

def delete_bucket_policy(bucket_name):
    try:
        s3 = session.client('s3', endpoint_url=endpoint_url)
        response = s3.delete_bucket_policy(Bucket=bucket_name)
        print("delete_bucket_policy response:\n", response)

    except botocore.exceptions.ClientError as err:
        status = err.response["ResponseMetadata"]["HTTPStatusCode"]
        errcode = err.response["Error"]["Code"]
        if status == 404:
            logging.warning("Missing object, %s", errcode)
        elif status == 403:
            logging.error("Access denied, %s", errcode)
        else:
            logging.exception("Error in request, %s", errcode)
    return {}

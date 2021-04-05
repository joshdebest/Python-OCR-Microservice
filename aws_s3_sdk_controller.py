import io
import logging
import boto3
import botocore
import cv2
import numpy as np


class AwsS3SdkController:

    session = None
    localhost_url_endpoint = ""

    def __init__(self):
        self.session = boto3.Session(aws_access_key_id="",
                                     aws_secret_access_key="",
                                     region_name="",
                                     )

    def get_matching_s3_objects(self, bucket_name, prefix="", suffix=""):
        """
        Generate objects in an S3 bucket.

        :param bucket_name: Name of the S3 bucket.
        :param prefix: Only fetch objects whose key starts with
            this prefix (optional).
            this suffix (optional).
        """
        s3 = self.session.client('s3', endpoint_url=self.localhost_url_endpoint)
        paginator = s3.get_paginator("list_objects_v2")

        kwargs = {'Bucket': bucket_name}

        # We can pass the prefix directly to the S3 API.  If the user has passed
        # a tuple or list of prefixes, we go through them one by one.
        if isinstance(prefix, str):
            prefixes = (prefix,)
        else:
            prefixes = prefix

        for key_prefix in prefixes:
            kwargs["Prefix"] = key_prefix

            for page in paginator.paginate(**kwargs):
                try:
                    contents = page["Contents"]
                except KeyError:
                    break

                for obj in contents:
                    key = obj["Key"]
                    if key.endswith(suffix):
                        yield obj

    def list_all_objects_in_specified_bucket(self, bucket_name, prefix="", suffix=""):
        try:
            array = []
            for key in self.get_matching_s3_keys(bucket_name, prefix, suffix):
                array.append(key)
            return array
        except botocore.exceptions.ClientError as err:
            status = err.response["ResponseMetadata"]["HTTPStatusCode"]
            errcode = err.response["Error"]["Code"]
            if status == 404:
                logging.warning("Missing object, %s", errcode)
            elif status == 403:
                logging.error("Access denied, %s", errcode)
            else:
                logging.exception("Error in request, %s", errcode)
        return array

    def list_all_s3_buckets(self):
        try:
            s3 = self.session.client('s3', endpoint_url=self.localhost_url_endpoint)
            response = s3.list_buckets()
            print("Existing buckets: ")
            for bucket in response['Buckets']:
                print("----", f'{bucket["Name"]}')
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

    def create_new_bucket(self, bucket_name, region=None):
        # Create bucket
        try:
            if region is None:
                s3_client = self.session.client('s3', endpoint_url=self.localhost_url_endpoint)
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                s3_client = self.session.client('s3', region_name=region, endpoint_url=self.localhost_url_endpoint)
                location = {'LocationConstraint': region}
                s3_client.create_bucket(Bucket=bucket_name,
                                        CreateBucketConfiguration=location)
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

    def download_specific_s3_file(self, bucket_name, object_name):
        downloaded_object = None
        try:

            s3 = self.session.client('s3', endpoint_url=self.localhost_url_endpoint)
            outfile = io.BytesIO()
            with open('FILE_NAME', 'wb'):
                s3.download_fileobj(bucket_name, object_name, outfile)
            outfile.seek(0)
            file_bytes = np.asarray(bytearray(outfile.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
            # cv2.imshow(object_name, img)
            return img


        except botocore.exceptions.ClientError as err:
            status = err.response["ResponseMetadata"]["HTTPStatusCode"]
            errcode = err.response["Error"]["Code"]
            if status == 404:
                logging.warning("Missing object, %s", errcode)
            elif status == 403:
                logging.error("Access denied, %s", errcode)
            else:
                logging.exception("Error in request, %s", errcode)
        return downloaded_object

    def upload_file_to_aws_s3(self, file, bucket, file_name):
        """Upload a file to an S3 bucket

        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """

        # Upload the file
        s3 = self.session.client('s3', endpoint_url=self.localhost_url_endpoint)
        try:
            with open("backups/FILE_NAME", "rb") as f:
                s3.upload_fileobj(f, bucket, file_name)
        except botocore.exceptions.ClientError as err:
            status = err.response["ResponseMetadata"]["HTTPStatusCode"]
            errcode = err.response["Error"]["Code"]
            if status == 404:
                logging.warning("Missing object, %s", errcode)
            elif status == 403:
                logging.error("Access denied, %s", errcode)
            else:
                logging.exception("Error in request, %s", errcode)
        return True

    def get_matching_s3_keys(self, bucket_name, prefix="", suffix=""):
        """
        Generate the keys in an S3 bucket.

        :param bucket_name: Name of the S3 bucket.
        :param prefix: Only fetch keys that start with this prefix (optional).
        :param suffix: Only fetch keys that end with this suffix (optional).
        """
        for obj in self.get_matching_s3_objects(bucket_name, prefix, suffix):
            yield obj["Key"]

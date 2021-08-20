from json.decoder import JSONDecodeError
import logging
import boto3
from botocore.exceptions import ClientError
import json

client = boto3.client('s3', region_name='us-east-1')
resource = boto3.resource('s3', region_name='us-east-1')

s3_ef_ds_bucket = 's3500659-ef-deliverystream'


def get_trending_recipe_keys():
    """ get all keys from s3 trending recipes bucket """
    bucket = s3_ef_ds_bucket
    keys = []

    try:
        response = client.list_objects_v2(
            Bucket=bucket
        )

        if response['KeyCount'] == 0:
            return

        for item in response['Contents']:
            keys.append(item['Key'])
    except ClientError as e:
        return

    return keys


def get_trending_recipes():
    """ 
    extract trending recipe information from the S3 trending recipe bucket.

    returns: a list of trending recipes which may include duplicates.
    """
    decoder = json.JSONDecoder()
    recipes = set()

    keys = get_trending_recipe_keys()

    if keys is None:
        return

    for key in keys:
        obj = resource.Object(s3_ef_ds_bucket, key)

        content = obj.get()['Body'].read().decode('utf-8')

        content_length = len(content)
        decode_index = 0

        while decode_index < content_length:
            try:
                obj, decode_index = decoder.raw_decode(content, decode_index)
                recipes.add(obj['id'])
            except JSONDecodeError as e:
                # Scan forward and keep trying to decode
                decode_index += 1

    return recipes


def delete_recipe(bucket, key):
    """ delete a specified recipe from S3 bucket """
    resource.Object(bucket, key).delete()


def download_recipe(bucket, key):
    """ 
    downloads recipe from S3 bucket.

    returns: a json format version of the recipe.
    """
    content_object = resource.Object(bucket, key)
    file_content = content_object.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)

    return json_content


def check_recipe_exist(bucket, key):
    results = client.list_objects(Bucket=bucket, Prefix=key)
    return 'Contents' in results


def upload_recipe(object, bucket, key):
    """ upload the specified recipe to an S3 bucket """
    json_object = object
    client.put_object(
        Body=json.dumps(json_object),
        Bucket=bucket,
        Key=key
    )


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    try:
        response = client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def create_bucket(bucket_name, region=None):
    """Create an S3 bucket in a specified region

    If a region is not specified, the bucket is created in the S3 default
    region (us-east-1).

    :param bucket_name: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-west-2'
    :return: True if bucket created, else False
    """

    # Create bucket
    try:
        if region is None:
            client = boto3.client('s3')
            client.create_bucket(Bucket=bucket_name)
        else:
            client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            client.create_bucket(Bucket=bucket_name,
                                 CreateBucketConfiguration=location)
    except ClientError as e:
        logging.error(e)
        return False
    return True

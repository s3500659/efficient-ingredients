import boto3
import json

import botocore

client = boto3.client('kinesis', region_name='us-east-1')


def create_stream(name, shard):
    """ create a new AWS Kinesis Datastream """
    try:
        response = client.create_stream(
            StreamName=name,
            ShardCount=shard
        )
    except botocore.exceptions.ClientError as error:
        return


def put_record(name, data, key):
    """ put new record into the Kinesis Datastream"""
    response = client.put_record(
        StreamName=name,
        Data=json.dumps(data),
        PartitionKey=key)

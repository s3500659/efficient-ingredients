import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
client = boto3.client('dynamodb', region_name='us-east-1')
table_name = 'efficient_ingredients_user'
p_key = 'email'


def table_exist(table_name=table_name):
    tables = client.list_tables()['TableNames']
    if table_name not in tables:
        return False

    return True


def get_user(email):
    table = dynamodb.Table(table_name)

    try:
        response = table.get_item(
            Key={
                p_key: email
            }
        )
        item = response['Item']
    except ClientError:
        return None
    except KeyError:
        return None

    return item


def create_user(email, password, username):
    table = dynamodb.Table(table_name)

    table.put_item(
        Item={
            p_key: email,
            'password': password,
            'user_name': username
        }
    )


def create_user_table():

    # Create the DynamoDB table.
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': p_key,
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': p_key,
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    # Wait until the table exists.
    table.meta.client.get_waiter('table_exists').wait(TableName=table_name)

    return table

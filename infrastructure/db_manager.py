import boto3

client = boto3.client('dynamodb', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


def get_table(table_name):
    table = dynamodb.Table(table_name)
    return table


def table_exist(table_name):

    tables = client.list_tables()['TableNames']
    if table_name not in tables:
        return False

    return True


def create_table(name, p_key, s_key):

    if table_exist(name) == True:
        return

    # Create the DynamoDB table.
    table = dynamodb.create_table(
        TableName=name,
        KeySchema=[
            {
                'AttributeName': p_key,
                'KeyType': 'HASH'
            },
            {
                'AttributeName': s_key,
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': p_key,
                'AttributeType': 'S'
            },
            {
                'AttributeName': s_key,
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    # Wait until the table exists.
    table.meta.client.get_waiter('table_exists').wait(TableName=name)

    return table

import boto3
from boto3.dynamodb.conditions import Key, Attr


class DbPantry:
    def __init__(self, tableName: str):
        self.table_name = tableName
        self.resource = boto3.resource('dynamodb', region_name='us-east-1')
        self.client = boto3.client('dynamodb', region_name='us-east-1')
        self.table = self.resource.Table(self.table_name)


    def get_items(self, email):
        table = self.resource.Table(self.table_name)
        response = table.query(
            KeyConditionExpression=Key('email').eq(email)
        )
        items = response['Items']
        return items

    def delete_item(self, email, ingredient):
        self.table.delete_item(
            Key={
                'email': email,
                'ingredient': ingredient
            }
        )

    def get_item(self, email, ingredient):
        table = self.table
        
        response = table.get_item(
            Key={
                'email': email,
                'ingredient': ingredient
            }
        )
        
        item = response['Item']
        return item

    def add_item(self, email, name, expiry):
        table = self.table

        table.put_item(
            Item={
                'email': email,
                'ingredient': name,
                'expiry_date': expiry
            }
        )

    def table_exist(self, table_name):
        tables = self.client.list_tables()['TableNames']
        if table_name not in tables:
            return False

        return True

    def create_pantry(self):
        # Get the service resource.
        dynamodb = boto3.resource('dynamodb')
        pkey = 'email'
        skey = 'ingredient'

        if self.table_exist(self.table_name) == True:
            return
        # Create the DynamoDB table.
        table = dynamodb.create_table(
            TableName=self.table_name,
            KeySchema=[
                {
                    'AttributeName': pkey,
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': skey,
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': pkey,
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': skey,
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        # Wait until the table exists.
        table.meta.client.get_waiter('table_exists').wait(
            TableName=self.table_name)
        return table

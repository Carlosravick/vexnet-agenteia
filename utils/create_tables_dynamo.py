import boto3
import os

dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=os.getenv('DYNAMODB_ENDPOINT', 'http://localhost:8001'),
    region_name='us-west-2',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'fake'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'fake')
)

table_name = os.getenv('DYNAMODB_TABLE', 'clientes')

existing_tables = [t.name for t in dynamodb.tables.all()]
if table_name not in existing_tables:
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'telefone', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'telefone', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    table.wait_until_exists()
    print(f"Tabela '{table_name}' criada com sucesso!")
else:
    print(f"Tabela '{table_name}' já existe!")

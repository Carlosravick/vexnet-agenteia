import os
import json
import boto3

DYNAMODB_ENDPOINT = os.getenv('DYNAMODB_ENDPOINT', 'http://dynamodb-local:8000')
DYNAMODB_TABLE = os.getenv('DYNAMODB_TABLE', 'clientes')

dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=DYNAMODB_ENDPOINT,
    region_name='us-west-2',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'fake'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'fake')
)
table = dynamodb.Table(DYNAMODB_TABLE)

def get_cliente(telefone):
    resp = table.get_item(Key={'telefone': telefone})
    return resp.get('Item')

def save_cliente(telefone, cpf, nome=None, dados_cliente=None, cache_mensagens=0):
    item = {'telefone': telefone, 'cpf': cpf}
    if nome:
        item['nome'] = nome
    if dados_cliente:
        item['dados_cliente'] = json.dumps(dados_cliente)
        item['cache_mensagens'] = cache_mensagens
    table.put_item(Item=item)

def save_chat_history(telefone, history):
    table.update_item(
        Key={'telefone': telefone},
        UpdateExpression='SET chat_history = :h',
        ExpressionAttributeValues={':h': json.dumps(history)}
    )

def get_chat_history(telefone):
    resp = table.get_item(Key={'telefone': telefone})
    item = resp.get('Item')
    if item and 'chat_history' in item:
        return json.loads(item['chat_history'])
    return []

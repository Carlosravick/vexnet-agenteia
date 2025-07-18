import json
from utils.dynamo_utils import get_cliente, save_cliente
from app.tools.client_api import get_client_data_by_cpf, filtrar_dados_cliente

async def obter_dados_cliente(telefone, cpf):
    dados = get_cliente(telefone)
    cache_limit = 5
    # Se não há cache, cpf mudou ou passou limite, consulta API
    if (
        not dados or
        dados.get('cpf') != cpf or
        int(dados.get('cache_mensagens', 0)) >= cache_limit or
        not dados.get('dados_cliente')
    ):
        dados_api = await get_client_data_by_cpf(cpf)
        dados_filtrados = filtrar_dados_cliente(dados_api)
        save_cliente(telefone, cpf, nome=dados_filtrados.get('nome'), dados_cliente=dados_filtrados, cache_mensagens=1)
        return dados_filtrados
    else:
        # Incrementa contador de cache e retorna cache
        save_cliente(
            telefone,
            cpf,
            nome=dados.get('nome'),
            dados_cliente=json.loads(dados['dados_cliente']),
            cache_mensagens=int(dados.get('cache_mensagens', 0)) + 1
        )
        return json.loads(dados['dados_cliente'])

import os
import httpx

async def get_client_data_by_cpf(cpf: str) -> dict:
    cpf_cleaned = "".join(filter(str.isdigit, cpf))
    api_url = f"{os.getenv('CLIENT_API_URL')}?cpf={cpf_cleaned}"
    api_user = os.getenv("CLIENT_API_USER")
    api_password = os.getenv("CLIENT_API_PASSWORD")
    if not api_user or not api_password:
        return {"error": "Credenciais da API interna não configuradas."}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                api_url,
                auth=(api_user, api_password),
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            return {"error": "Timeout"}
        except httpx.RequestError as e:
            return {"error": str(e)}

def filtrar_dados_cliente(dados_api):
    dados_cliente = dados_api.get('Dados_do_Cliente', {}).get('body', {})
    status = dados_cliente.get('status', None)
    nome = dados_cliente.get('name', '')
    inadimplencia = dados_api.get('Verificar_inadimplencia', {}).get('body', {}).get('Mensagem', '')
    alerta = dados_api.get('Alertas_de_Falha_em_Regiao', {}).get('body', {}).get('Mensagem', '')
    historico = dados_api.get('Historico_OS_Cliente', {}).get('data', [])
    ultimo_chamado = None
    for h in historico:
        if "Manutenção" in h['title'] or "Sem Internet" in h['title']:
            ultimo_chamado = {
                'protocolo': h.get('protocol'),
                'status': h.get('status'),
                'inicio': h.get('beginningData'),
                'fim': h.get('finalData'),
                'resumo': h['movimentacoes'][-1]['description'] if h.get('movimentacoes') else ""
            }
            break
    return {
        "nome": nome,
        "status_plano": status,
        "inadimplencia": inadimplencia,
        "alerta_regiao": alerta,
        "ultimo_chamado": ultimo_chamado
    }

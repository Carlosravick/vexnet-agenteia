import httpx
import os
from langchain.tools import tool

@tool
async def get_client_data_by_cpf(cpf: str) -> dict:
    """Usa o CPF de um cliente para buscar seus dados no banco de dados, autenticando com usuário e senha."""
    
    cpf_cleaned = "".join(filter(str.isdigit, cpf))
    api_url = f"{os.getenv('CLIENT_API_URL')}?cpf={cpf_cleaned}"
    
    api_user = os.getenv("CLIENT_API_USER")
    api_password = os.getenv("CLIENT_API_PASSWORD")

    if not api_user or not api_password:
        return {"error": "Credenciais da API interna não configuradas."}

    print(f"Buscando dados na API para o CPF: {cpf_cleaned}")

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
            print("ERRO: A API de clientes demorou muito para responder (Timeout).")
            return {"error": "O sistema de clientes demorou muito para responder."}
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return {"error": "Falha na autenticação com a API interna."}
            return {"error": f"Erro HTTP ao acessar a API: {e.response.status_code}"}

        except httpx.RequestError as e:
            return {"error": f"Não foi possível conectar à API de clientes: {e}"}
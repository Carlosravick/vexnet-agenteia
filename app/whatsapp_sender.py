import httpx
import os

async def send_whatsapp_message(to_number: str, message_body: str):
    """
    Envia uma mensagem de resposta para o WhatsApp usando httpx.
    """
    provider_url = os.getenv('WHATSAPP_PROVIDER_URL')
    token = os.getenv('WHATSAPP_PROVIDER_TOKEN')
    
    if not provider_url or not token:
        print("ERRO: URL ou Token do provedor do WhatsApp não configurado no .env")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    # O payload pode variar um pouco dependendo do provedor (Twilio, Meta, etc.)
    # Este exemplo é baseado no formato da API da Meta.
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number.replace('whatsapp:', ''), # Garante que não tenha o prefixo
        "text": {"body": message_body}
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(provider_url, json=payload, headers=headers)
            response.raise_for_status()
            print(f"Mensagem de resposta enviada para {to_number}. Status: {response.status_code}")
        except httpx.RequestError as e:
            print(f"Erro ao enviar mensagem de resposta via WhatsApp: {e}")
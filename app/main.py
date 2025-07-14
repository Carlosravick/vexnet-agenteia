from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import re

load_dotenv()

from app.agent_logic import run_agent_logic 

app = FastAPI()

# --- Modelos Pydantic (não mudam) ---
class BotRequest(BaseModel):
    user_id: str
    user_message: str
    chat_history: str = ""

class BotResponse(BaseModel):
    reply_text: str

# --- O Roteador de Intenção ---
def is_internet_issue(message: str) -> bool:
    """
    Verifica se a mensagem do usuário parece ser sobre um problema de internet.
    Usa uma lista de palavras-chave para fazer essa verificação.
    """
    # Lista de palavras-chave que acionam o bot
    keywords = [
        "internet", "conexão", "conexao", "sinal", "wifi", "wi-fi",
        "não funciona", "nao funciona", "sem sinal", "caiu", "lenta",
        "devagar", "problema", "falta", "instavel"
    ]
    # Expressão regular para encontrar palavras inteiras, ignorando maiúsculas/minúsculas
    pattern = r'\b(' + '|'.join(keywords) + r')\b'
    if re.search(pattern, message.lower()):
        return True
    return False

# --- Endpoint Principal Atualizado ---
@app.post("/gerar_resposta", response_model=BotResponse)
async def gerar_resposta(request: BotRequest):
    print(f"Requisição recebida para o usuário {request.user_id}: '{request.user_message}'")

    if is_internet_issue(request.user_message):
        print("Problema de internet detectado. Acionando o agente de IA.")
        
        response_text = await run_agent_logic(
            input_message=request.user_message,
            client_id=request.user_id,
            chat_history=request.chat_history
        )
        
        # NOSSO "DETECTOR DE ERROS"
        if response_text is None:
            print("ERRO GRAVE: A função run_agent_logic retornou um valor NULO (None).")
            # Retornamos uma resposta segura para não dar o erro 500
            return BotResponse(reply_text="Desculpe, encontrei um erro inesperado ao processar. Tente novamente.")
            
        return BotResponse(reply_text=response_text)
    else:
        print("Mensagem não relacionada a problemas de internet. Retornando resposta padrão.")
        default_reply = "Olá! Sou o assistente virtual da Vexnet. Se estiver com problemas na sua conexão de internet, por favor, me diga para que eu possa ajudar."
        return BotResponse(reply_text=default_reply)

def is_internet_issue(message: str) -> bool:
    """
    Verifica se a mensagem do usuário parece ser sobre um problema de internet.
    Usa a lista de palavras-chave da Base de Conhecimento Vexnet.
    """
    # Lista de palavras-chave e gatilhos da sua documentação
    keywords = [
        "sem internet", "sem conexão", "conexao", "led vermelho", "wifi não aparece",
        "internet caiu", "conexão voltou mas está ruim", "desliguei e não volta",
        "reiniciei e não volta", "sem sinal", "cortaram o fio", "manutenção na rua",
        "quando volta", "roteador apagado", "sem luz", "paguei e não voltou",
        "nome do meu wifi mudou", "resetei o roteador"
    ]
    # Expressão regular para encontrar as frases ou palavras, ignorando maiúsculas/minúsculas
    pattern = r'(' + '|'.join(keywords) + r')'
    if re.search(pattern, message.lower()):
        return True
    return False

@app.get("/")
def read_root():
    return {"Status": "API do Agente de Atendimento Ativa"}
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
from app.agent_logic import run_agent_logic

app = FastAPI()

class BotRequest(BaseModel):
    user_id: str
    cpf: str
    user_message: str

class BotResponse(BaseModel):
    reply_text: str

@app.post("/gerar_resposta", response_model=BotResponse)
async def gerar_resposta(request: BotRequest):
    response_text = await run_agent_logic(
        input_message=request.user_message,
        client_id=request.user_id,
        cpf_post=request.cpf
    )
    if response_text is None:
        return BotResponse(reply_text="Desculpe, encontrei um erro inesperado ao processar. Tente novamente.")
    return BotResponse(reply_text=response_text)

@app.get("/")
def read_root():
    return {"Status": "API do Agente de Atendimento Ativa"}

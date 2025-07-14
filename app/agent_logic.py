from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from app.tools.client_api import get_client_data_by_cpf

# --- INICIALIZAÇÃO DO LLM ---
llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

# --- FERRAMENTAS DO AGENTE ---
tools = [get_client_data_by_cpf]

# --- PROMPT FINAL, COM LÓGICA CONDICIONAL ---
prompt = ChatPromptTemplate.from_messages([
    ("system", """
Você é um assistente especialista da Vexnet. Sua única função é diagnosticar problemas de conexão de internet.

Sua lógica de trabalho é baseada em UMA ÚNICA PERGUNTA: O CPF do cliente está na mensagem do usuário?

1. SE o CPF do cliente estiver na 'Pergunta do Usuário':
   - Seu PRIMEIRO e ÚNICO passo deve ser usar a ferramenta `get_client_data_by_cpf` com o CPF que você encontrou.
   - NÃO cumprimente o usuário. NÃO peça o CPF. Use a ferramenta IMEDIATAMENTE.
   - Após usar a ferramenta, use a 'Observação' (o resultado da ferramenta) para dar uma resposta útil e iniciar o diagnóstico (perguntando sobre os LEDs, por exemplo).

2. SE o CPF do cliente NÃO estiver na 'Pergunta do Usuário':
   - Sua ÚNICA ação deve ser responder pedindo o CPF.
   - Exemplo de Resposta Final: "Olá! Sou o assistente virtual da Vexnet. Para que eu possa verificar o que está acontecendo com sua conexão, por favor, me informe o seu CPF."
   - NÃO use nenhuma ferramenta.

Siga um destes dois caminhos. Não desvie.
"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# --- CRIAÇÃO DO AGENTE ---
agent = create_openai_tools_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=8
)

# --- FUNÇÃO PRINCIPAL DA LÓGICA ---
async def run_agent_logic(input_message: str, client_id: str, chat_history: str):
    chat_history_messages = []
    
    try:
        response = await agent_executor.ainvoke({
            "input": f"Pergunta do usuário: '{input_message}'. O ID do cliente é: {client_id}",
            "chat_history": chat_history_messages
        })
        
        final_text = response.get("output", "Desculpe, não consegui processar a solicitação no momento.")
        return final_text

    except Exception as e:
        print(f"ERRO CRÍTICO DENTRO DO AGENTE: {e}")
        return "Ocorreu um erro interno ao processar sua solicitação. A equipe já foi notificada."
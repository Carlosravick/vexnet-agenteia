import re
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from app.tools.client_api import get_client_data_by_cpf

# --- INICIALIZAÇÃO DO LLM ---
llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", max_tokens=150) # max_tokens ajustado

# --- FERRAMENTAS DO AGENTE ---
tools = [get_client_data_by_cpf]

# --- PROMPT FINAL ---
# O prompt que você criou está excelente e não precisa de mudanças.
prompt = ChatPromptTemplate.from_messages([
    ("system", """
Você é um assistente especialista da Vexnet. Sua única função é diagnosticar problemas de conexão de internet.

---
### REGRAS DE RACIOCÍNIO:
Sua lógica de trabalho é baseada em UMA ÚNICA PERGUNTA: O CPF do cliente está na mensagem do usuário?

1.  **SE o CPF do cliente estiver na 'Pergunta do Usuário':**
    -   Seu PRIMEIRO e ÚNICO passo deve ser usar a ferramenta `get_client_data_by_cpf` com o CPF que você encontrou.
    -   NÃO cumprimente o usuário. NÃO peça o CPF. Use a ferramenta IMEDIATAMENTE.
    -   Use a 'Observação' (o resultado da ferramenta) para obter o contexto sobre o cliente.

2.  **SE o CPF do cliente NÃO estiver na 'Pergunta do Usuário':**
    -   Sua ÚNICA ação deve ser responder pedindo o CPF.
    -   NÃO use nenhuma ferramenta.

---
### FORMATO DA RESPOSTA FINAL (MUITO IMPORTANTE):
Sua resposta final deve ser **APENAS o texto para o cliente**, como se você estivesse conversando diretamente com ele no WhatsApp.
NUNCA inclua descrições do que você está fazendo (como "Vou usar a ferramenta..." ou "A ferramenta retornou...").

-   **Exemplo de Resposta Final (SE VOCÊ PEDIU O CPF):**
    "Olá! Sou o assistente virtual da Vexnet. Para que eu possa verificar o que está acontecendo com sua conexão, por favor, me informe o seu CPF."

-   **Exemplo de Resposta Final (SE VOCÊ USOU A FERRAMENTA E A OBSERVAÇÃO FOI 'Cliente com débitos pendentes'):**
    "Olá! Verifiquei aqui pelo seu CPF e notei que existem débitos pendentes em seu cadastro. A falta de conexão pode estar relacionada a isso. Você pode verificar os detalhes em nosso portal do cliente."

-   **Exemplo de Resposta Final (SE VOCÊ USOU A FERRAMENTA E A OBSERVAÇÃO FOI 'Cliente sem débitos, plano ativo'):**
    "Olá! Verifiquei aqui e seu plano está ativo e sem pendências. Para iniciarmos o diagnóstico, por favor, me informe como estão as luzes do seu roteador."

Fale diretamente com o cliente. Gere apenas a resposta final.
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

# --- 1. MEMÓRIA DE CONVERSA (EM MEMÓRIA) ---
chat_histories = {}

# --- 3. FUNÇÃO AUXILIAR PARA EXTRAIR CPF ---
def extract_cpf_from_message(message: str) -> str | None:
    """Usa uma expressão regular para encontrar uma sequência de 11 dígitos (um CPF) na mensagem."""
    match = re.search(r'\b\d{11}\b', message)
    if match:
        return match.group(0)
    return None

# --- FUNÇÃO PRINCIPAL DA LÓGICA (CORRIGIDA) ---
async def run_agent_logic(input_message: str, client_id: str, chat_history: str):
    
    # Recupera o histórico da conversa para este cliente
    current_chat_history = chat_histories.get(client_id, [])
    
    # 2. CONTROLE DE LIMITE DE CONTEXTO (JANELA DESLIZANTE)
    # Garante que o histórico não fique grande demais, mantendo as últimas 10 mensagens
    if len(current_chat_history) > 10:
        current_chat_history = current_chat_history[-10:]
    
    # 3. DETECÇÃO CONFIÁVEL DE CPF
    # Tentamos extrair o CPF da mensagem do usuário antes de chamar a IA
    cpf_encontrado = extract_cpf_from_message(input_message)
    
    if cpf_encontrado:
        # Se um CPF foi encontrado, damos uma instrução direta para a IA
        input_para_agente = (
            f"O CPF do cliente foi identificado como {cpf_encontrado}. "
            f"Use a ferramenta get_client_data_by_cpf para buscar os dados dele. "
            f"Depois, use o resultado para responder à pergunta original do usuário: '{input_message}'"
        )
    else:
        # Se não, deixamos a IA seguir o fluxo normal de pedir o CPF
        input_para_agente = f"Pergunta do usuário: '{input_message}'. O ID do cliente é: {client_id}"

    try:
        response = await agent_executor.ainvoke({
            "input": input_para_agente,  # Usamos nosso input inteligente
            "chat_history": current_chat_history
        })
        
        final_text = response.get("output", "Desculpe, não consegui processar a solicitação no momento.")
        
        # Atualiza o histórico com a nova interação
        current_chat_history.append(HumanMessage(content=input_message))
        current_chat_history.append(AIMessage(content=final_text))
        
        # Salva o histórico atualizado de volta na memória
        chat_histories[client_id] = current_chat_history
        
        return final_text

    except Exception as e:
        print(f"ERRO CRÍTICO DENTRO DO AGENTE: {e}")
        return "Ocorreu um erro interno ao processar sua solicitação. A equipe já foi notificada."
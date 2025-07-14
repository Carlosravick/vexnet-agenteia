# 🚀 Agentes IA com FastAPI

Este projeto implementa agentes utilizando FastAPI. Ele expõe uma API que pode ser acessada publicamente via ngrok.

## ⚙️ Requisitos

- Python 3.10+
- [ngrok](https://ngrok.com/) instalado e autenticado (opcionalmente via `ngrok config add-authtoken`)

## 📁 Clonando o Repositório

```bash
git clone https://https://github.com/Carlosravick/vexnet-agenteia
cd vexnet-agenteIA
```

## 🔐 Configuração do Ambiente

Crie um arquivo `.env` com base no modelo abaixo:

```env
# .env.example
OPENAI_API_KEY=your_api_key_here
# outros parâmetros se necessário
```

> ⚠️ Não edite o `.env.example`. Crie um novo `.env` baseado nele.

## 📦 Instalação das Dependências

Crie um ambiente virtual (opcional, mas recomendado):

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## ▶️ Executando a API

Inicie o servidor FastAPI:

```bash
uvicorn app:main --reload
```

Em seguida, em outro terminal, execute o ngrok:

```bash
ngrok http 8000
```

Você verá um link do tipo `https://xxxx.ngrok.io`, que será o endpoint público da sua API.

## 📫 Contato

Dúvidas ou sugestões? Abra uma issue ou entre em contato via [meu LinkedIn](https://www.linkedin.com/in/carlosravick/)
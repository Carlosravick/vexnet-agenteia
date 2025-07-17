# 1. Imagem Base
FROM python:3.13-slim

# 2. Variáveis de Ambiente Essenciais
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Diretório de Trabalho
# Criamos um diretório genérico para o nosso código
WORKDIR /code

# 4. A CORREÇÃO MAIS IMPORTANTE
# Dizemos ao Python para procurar módulos a partir do nosso diretório de trabalho.
# É isso que faz o "from app..." funcionar.
ENV PYTHONPATH /code

# 5. Instalação de Dependências
# Copiamos apenas o requirements.txt primeiro para otimizar o cache do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Cópia do Código da Aplicação
# Copiamos a sua pasta 'app' para dentro do diretório de trabalho
COPY ./app /code/app

# 7. Exposição da Porta
EXPOSE 8000

# 8. Comando de Execução
# O comando original agora funciona porque o PYTHONPATH está correto
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
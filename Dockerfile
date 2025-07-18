FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

ENV PYTHONPATH /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /code/app
COPY ./utils /code/utils

EXPOSE 8000

CMD ["sh", "-c", "python /code/utils/create_tables_dynamo.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]

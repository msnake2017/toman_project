FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN pip install -r requirements.txt

RUN chmod +x ./entrypoint.sh

CMD ["./entrypoint.sh"]

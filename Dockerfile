FROM python:3.10.9-slim-buster

RUN mkdir src

COPY requirements.txt src
COPY app src/app
COPY main.py src
COPY openssl src/openssl

WORKDIR src
RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 8100
CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8100"]

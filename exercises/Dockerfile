FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential cmake git \
    && rm -rf /var/lib/apt/lists/*

COPY runner/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Image autonome : le code de l'appli ET le contenu pedagogique (exercices,
# corrections, stubs de reinitialisation) sont copies dans l'image. Aucun
# bind mount n'est necessaire pour lancer l'atelier ailleurs.
COPY runner/app ./app
COPY workspace ./workspace
COPY solutions ./solutions
COPY stubs ./stubs

EXPOSE 8100

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100"]

# Použití oficiálního Python obrázku
FROM python:3.9-slim

# Nastavení pracovní složky
WORKDIR /app

# Kopírování requirements.txt a instalace závislostí
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Kopírování všech souborů aplikace do kontejneru
COPY . .

# Nastavení environment variable pro Flask
ENV FLASK_APP=main

# Otevření portu 5432 pro Flask server
EXPOSE 5432

# Spuštění Flask serveru
CMD ["flask", "run", "--host=0.0.0.0", "--port=5432", "--reload"]

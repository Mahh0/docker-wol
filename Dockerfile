# Utiliser l'image de base compatible ARM pour Raspberry Pi
FROM python:3.9-slim-buster

# Répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers nécessaires dans le conteneur
COPY requirements.txt .
COPY app.py .
COPY templates templates
COPY static static

# Installer les dépendances Python
RUN apt-get update && apt-get install -y net-tools && pip install --no-cache-dir -r requirements.txt

# Exposer le port 80
EXPOSE 80
EXPOSE 5000

# Commande à exécuter lors du démarrage du conteneur
CMD ["python", "app.py"]
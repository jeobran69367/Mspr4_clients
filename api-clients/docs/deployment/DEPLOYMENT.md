# Guide de déploiement

## 🚀 Déploiement en production

### Prérequis

- Serveur Linux (Ubuntu 20.04+ recommandé)
- Docker & Docker Compose
- Accès SSH au serveur
- Nom de domaine configuré
- Certificat SSL (Let's Encrypt recommandé)

## 📦 Déploiement avec Docker

### 1. Préparation du serveur

```bash
# Connexion au serveur
ssh user@your-server.com

# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation de Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Installation de Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Création du répertoire de déploiement
sudo mkdir -p /opt/payetonkawa
sudo chown $USER:$USER /opt/payetonkawa
```

### 2. Configuration de l'environnement

```bash
cd /opt/payetonkawa

# Cloner le repository
git clone https://github.com/jeobran69367/Mspr4_clients.git
cd Mspr4_clients/api-clients

# Créer le fichier .env de production
cat > .env << EOF
# Database
DATABASE_URL=postgresql://payetonkawa:STRONG_PASSWORD_HERE@postgres:5432/payetonkawa_clients
DATABASE_HOST=postgres
DATABASE_PORT=5432
DATABASE_USER=payetonkawa
DATABASE_PASSWORD=STRONG_PASSWORD_HERE
DATABASE_NAME=payetonkawa_clients

# Application
APP_NAME=PayeTonKawa - Service Clients
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=production

# Security - CHANGEZ CES VALEURS
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=payetonkawa
RABBITMQ_PASSWORD=STRONG_PASSWORD_HERE
RABBITMQ_VHOST=/

# CORS
CORS_ORIGINS=https://payetonkawa.fr,https://api.payetonkawa.fr

# API
API_V1_PREFIX=/api/v1
EOF

# Sécuriser le fichier
chmod 600 .env
```

### 3. Configuration Docker Compose pour production

Créer `docker-compose.prod.yml` :

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_DB: ${DATABASE_NAME}
      POSTGRES_USER: ${DATABASE_USER}
      POSTGRES_PASSWORD: ${DATABASE_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - payetonkawa-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DATABASE_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  rabbitmq:
    image: rabbitmq:3-management-alpine
    restart: always
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_USER}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD}
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    networks:
      - payetonkawa-network
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    restart: always
    env_file: .env
    depends_on:
      postgres:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    networks:
      - payetonkawa-network
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    networks:
      - payetonkawa-network

volumes:
  postgres_data:
  rabbitmq_data:

networks:
  payetonkawa-network:
    driver: bridge
```

### 4. Configuration Nginx

Créer `nginx.conf` :

```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    server {
        listen 80;
        server_name api.payetonkawa.fr;
        
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        
        location / {
            return 301 https://$server_name$request_uri;
        }
    }

    server {
        listen 443 ssl http2;
        server_name api.payetonkawa.fr;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        client_max_body_size 10M;

        location / {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /health {
            proxy_pass http://api/health;
            access_log off;
        }
    }
}
```

### 5. Obtention du certificat SSL

```bash
# Installation de Certbot
sudo apt install certbot

# Obtention du certificat
sudo certbot certonly --standalone -d api.payetonkawa.fr

# Copier les certificats
sudo mkdir -p ssl
sudo cp /etc/letsencrypt/live/api.payetonkawa.fr/fullchain.pem ssl/
sudo cp /etc/letsencrypt/live/api.payetonkawa.fr/privkey.pem ssl/
sudo chown -R $USER:$USER ssl/

# Renouvellement automatique
sudo crontab -e
# Ajouter : 0 0 * * * certbot renew --quiet
```

### 6. Démarrage de l'application

```bash
# Build des images
docker-compose -f docker-compose.prod.yml build

# Démarrage des services
docker-compose -f docker-compose.prod.yml up -d

# Exécution des migrations
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head

# Vérification
docker-compose -f docker-compose.prod.yml ps
curl https://api.payetonkawa.fr/health
```

## 🔄 Mise à jour de l'application

```bash
cd /opt/payetonkawa/Mspr4_clients/api-clients

# Récupérer les dernières modifications
git pull origin main

# Reconstruire l'image
docker-compose -f docker-compose.prod.yml build api

# Arrêt gracieux
docker-compose -f docker-compose.prod.yml stop api

# Exécution des migrations
docker-compose -f docker-compose.prod.yml run --rm api alembic upgrade head

# Redémarrage
docker-compose -f docker-compose.prod.yml up -d api

# Vérification
docker-compose -f docker-compose.prod.yml logs -f api
```

## 📊 Monitoring et logs

### Consultation des logs

```bash
# Logs de l'API
docker-compose -f docker-compose.prod.yml logs -f api

# Logs PostgreSQL
docker-compose -f docker-compose.prod.yml logs -f postgres

# Logs RabbitMQ
docker-compose -f docker-compose.prod.yml logs -f rabbitmq

# Logs Nginx
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### Sauvegardes

```bash
# Backup PostgreSQL
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U payetonkawa payetonkawa_clients > backup_$(date +%Y%m%d_%H%M%S).sql

# Restauration
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U payetonkawa payetonkawa_clients < backup.sql
```

## 🔐 Sécurité en production

### 1. Firewall

```bash
# Installation UFW
sudo apt install ufw

# Configuration
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Fail2Ban

```bash
# Installation
sudo apt install fail2ban

# Configuration
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Mots de passe forts

- Générer des mots de passe avec `openssl rand -base64 32`
- Ne jamais committer le fichier `.env`
- Utiliser un gestionnaire de secrets (Vault, AWS Secrets Manager)

## 🚨 Plan de reprise d'activité

### Sauvegarde quotidienne

```bash
# Script de backup automatique
cat > /opt/payetonkawa/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=/opt/payetonkawa/backups
DATE=$(date +%Y%m%d_%H%M%S)

# Créer le répertoire de backup
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker-compose -f /opt/payetonkawa/Mspr4_clients/api-clients/docker-compose.prod.yml exec -T postgres pg_dump -U payetonkawa payetonkawa_clients | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Nettoyer les anciens backups (garder 7 jours)
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete

# Upload vers S3 (optionnel)
# aws s3 cp $BACKUP_DIR/db_$DATE.sql.gz s3://payetonkawa-backups/
EOF

chmod +x /opt/payetonkawa/backup.sh

# Ajouter au cron
crontab -e
# Ajouter : 0 2 * * * /opt/payetonkawa/backup.sh
```

## 📈 Performance

### Optimisation PostgreSQL

```sql
-- Dans postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
```

### Scaling horizontal

Pour augmenter la capacité, augmenter le nombre de workers :

```yaml
api:
  command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 8
```

## ✅ Checklist de déploiement

- [ ] Serveur configuré et sécurisé
- [ ] Docker et Docker Compose installés
- [ ] Certificat SSL obtenu
- [ ] Fichier .env configuré avec mots de passe forts
- [ ] Firewall activé
- [ ] Nginx configuré
- [ ] Application démarrée
- [ ] Migrations exécutées
- [ ] Sauvegarde automatique configurée
- [ ] Monitoring en place
- [ ] Tests de charge effectués
- [ ] Documentation à jour

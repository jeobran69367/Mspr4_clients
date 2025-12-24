# Quick Start Guide - Service Clients

## 🚀 Démarrage rapide (5 minutes)

### Option 1 : Docker Compose (Recommandé)

```bash
cd api-clients

# Démarrer tous les services (PostgreSQL, RabbitMQ, API)
docker-compose up -d

# Attendre que les services démarrent (30 secondes)
sleep 30

# Exécuter les migrations
docker-compose exec api alembic upgrade head

# Charger les données de test
docker-compose exec api python scripts/seed_data.py

# Vérifier que tout fonctionne
curl http://localhost:8001/health
```

L'API est maintenant disponible sur `http://localhost:8001`

### Option 2 : Installation locale

```bash
cd api-clients

# Créer et activer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate sur Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer l'environnement
cp .env.template .env
# Éditer .env avec vos paramètres

# Lancer PostgreSQL et RabbitMQ
docker-compose up -d postgres rabbitmq

# Exécuter les migrations
alembic upgrade head

# Charger les données de test
python scripts/seed_data.py

# Lancer le serveur
uvicorn app.main:app --reload
```

## 📝 Tester l'API

### 1. Créer un compte client

```bash
curl -X POST http://localhost:8001/api/v1/customers/ \
  -H "Content-Type: application/json" \
  -d '{
    "civilite": "M",
    "nom": "Dupont",
    "prenom": "Jean",
    "email": "jean.dupont@example.com",
    "telephone": "0612345678",
    "type_client": "particulier",
    "password": "monmotdepasse123"
  }'
```

### 2. Se connecter

```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jean.dupont@example.com",
    "password": "monmotdepasse123"
  }'
```

Récupérez le `access_token` de la réponse.

### 3. Obtenir son profil

```bash
curl -X GET http://localhost:8001/api/v1/customers/me \
  -H "Authorization: Bearer VOTRE_TOKEN_ICI"
```

### 4. Ajouter une adresse

```bash
curl -X POST http://localhost:8001/api/v1/addresses/ \
  -H "Authorization: Bearer VOTRE_TOKEN_ICI" \
  -H "Content-Type: application/json" \
  -d '{
    "type_adresse": "livraison",
    "est_defaut": true,
    "libelle": "Domicile",
    "destinataire": "Jean Dupont",
    "adresse_ligne1": "123 Rue de la Paix",
    "code_postal": "75001",
    "ville": "Paris",
    "pays": "France"
  }'
```

## 🔍 Explorer l'API

Accédez à la documentation interactive :

- **Swagger UI** : http://localhost:8001/docs
- **ReDoc** : http://localhost:8001/redoc

## 🧪 Comptes de test

Utilisez ces comptes pour tester (après `seed_data.py`) :

```
Admin :
  Email : admin@payetonkawa.fr
  Password : admin123

Client particulier :
  Email : marie.dupont@example.com
  Password : password123

Client professionnel :
  Email : contact@cafepro.fr
  Password : password123
```

## 🛠️ Commandes utiles

```bash
# Voir les logs
docker-compose logs -f api

# Arrêter les services
docker-compose down

# Redémarrer l'API
docker-compose restart api

# Exécuter les tests
docker-compose exec api pytest

# Accéder au shell Python
docker-compose exec api python

# Accéder à la base de données
docker-compose exec postgres psql -U payetonkawa -d payetonkawa_clients
```

## 🐛 Dépannage

### Le serveur ne démarre pas

```bash
# Vérifier les logs
docker-compose logs api

# Vérifier que PostgreSQL est prêt
docker-compose exec postgres pg_isready

# Redémarrer tous les services
docker-compose down
docker-compose up -d
```

### Erreur de base de données

```bash
# Supprimer et recréer la base
docker-compose down -v
docker-compose up -d
docker-compose exec api alembic upgrade head
docker-compose exec api python scripts/seed_data.py
```

### Port déjà utilisé

Modifiez les ports dans `docker-compose.yml` :
- API : `8000:8000` → `8001:8000`
- PostgreSQL : `5432:5432` → `5433:5432`

## 📚 Prochaines étapes

1. Lisez le [README.md](README.md) complet
2. Explorez la documentation API
3. Consultez les exemples de tests dans `tests/`
4. Adaptez la configuration dans `.env`
5. Intégrez avec les autres microservices

## 💡 Conseils

- Utilisez Postman ou Insomnia pour tester l'API
- Activez le mode debug pour plus de détails : `DEBUG=True` dans `.env`
- Consultez les logs pour diagnostiquer les problèmes
- Les tokens JWT expirent après 30 minutes

## 🔗 Ressources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [RabbitMQ Tutorials](https://www.rabbitmq.com/getstarted.html)

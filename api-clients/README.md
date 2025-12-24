# Service Clients - PayeTonKawa ☕

Service de gestion des clients pour PayeTonKawa, importateur de café en France.

## 📋 Description

Service microservice dédié à la gestion des clients (particuliers et professionnels), incluant :

- Enregistrement et gestion des clients
- Gestion des adresses (livraison/facturation)
- Authentification et autorisation JWT
- Synchronisation avec autres services via RabbitMQ
- API RESTful avec FastAPI
- Base de données PostgreSQL

## 🏗️ Architecture

```
api-clients/
├── app/                    # Application principale
│   ├── api/               # Endpoints REST
│   ├── models/            # Modèles SQLAlchemy
│   ├── schemas/           # Schémas Pydantic
│   ├── services/          # Logique métier
│   ├── repositories/      # Accès données
│   ├── events/            # RabbitMQ
│   ├── security/          # Authentification
│   └── utils/             # Utilitaires
├── tests/                 # Tests automatisés
├── migrations/            # Migrations Alembic
├── scripts/               # Scripts utilitaires
└── docs/                  # Documentation
```

## 🚀 Installation

### Prérequis

- Python 3.11+
- PostgreSQL 15+
- RabbitMQ 3+
- Docker & Docker Compose (optionnel)

### Installation locale

```bash
# Cloner le repository
cd api-clients

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Copier le fichier de configuration
cp .env.template .env
# Éditer .env avec vos paramètres

# Initialiser la base de données
alembic upgrade head

# Charger les données de test
python scripts/seed_data.py
```

### Installation avec Docker

```bash
# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f api

# Arrêter les services
docker-compose down
```

**Note sur les ports:** Le Service Clients utilise les ports suivants pour éviter les conflits avec d'autres services PayeTonKawa :
- API: `8001` (au lieu de 8000)
- PostgreSQL: `5434` (au lieu de 5432)
- RabbitMQ: `5674` et `15674` (au lieu de 5672 et 15672)

## 🎯 Utilisation

### Démarrage du serveur

```bash
# Mode développement
make run
# ou
uvicorn app.main:app --reload

# Mode production
make run-prod
# ou
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

Une fois le serveur démarré, accédez à :

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## 🔑 Authentification

L'API utilise JWT pour l'authentification. Workflow :

1. Créer un compte : `POST /api/v1/customers/`
2. Se connecter : `POST /api/v1/auth/login`
3. Utiliser le token : `Authorization: Bearer <access_token>`

### Comptes de test

Après avoir exécuté `python scripts/seed_data.py` :

```
Admin:
- Email: admin@payetonkawa.fr
- Password: admin123

Client particulier:
- Email: marie.dupont@example.com
- Password: password123

Client professionnel:
- Email: contact@cafepro.fr
- Password: password123
```

## 📡 Endpoints principaux

### Clients

- `POST /api/v1/customers/` - Créer un client
- `GET /api/v1/customers/me` - Obtenir son profil
- `GET /api/v1/customers/{id}` - Obtenir un client
- `PUT /api/v1/customers/{id}` - Mettre à jour un client
- `DELETE /api/v1/customers/{id}` - Supprimer un client
- `GET /api/v1/customers/` - Lister les clients (admin)

### Adresses

- `POST /api/v1/addresses/` - Créer une adresse
- `GET /api/v1/addresses/` - Lister ses adresses
- `GET /api/v1/addresses/{id}` - Obtenir une adresse
- `PUT /api/v1/addresses/{id}` - Mettre à jour une adresse
- `DELETE /api/v1/addresses/{id}` - Supprimer une adresse
- `POST /api/v1/addresses/{id}/set-default` - Définir par défaut

### Authentification

- `POST /api/v1/auth/login` - Se connecter
- `POST /api/v1/auth/refresh` - Rafraîchir le token
- `POST /api/v1/auth/change-password` - Changer le mot de passe
- `POST /api/v1/auth/confirm-email` - Confirmer l'email
- `POST /api/v1/auth/logout` - Se déconnecter

### Administration

- `POST /api/v1/admin/customers/{id}/activate` - Activer un client
- `POST /api/v1/admin/customers/{id}/suspend` - Suspendre un client
- `GET /api/v1/admin/stats` - Obtenir les statistiques

## 🧪 Tests

```bash
# Lancer tous les tests
make test

# Tests avec couverture
make test-cov

# Tests spécifiques
pytest tests/test_customers.py
pytest tests/test_auth.py -v
```

## 🔧 Développement

### Commandes Make

```bash
make help          # Afficher l'aide
make install       # Installer les dépendances
make dev           # Installer les dépendances de dev
make test          # Lancer les tests
make lint          # Linter le code
make format        # Formater le code
make docker-up     # Démarrer Docker
make migrate       # Lancer les migrations
make seed          # Charger les données de test
```

### Migrations de base de données

```bash
# Créer une migration
alembic revision --autogenerate -m "Description"
# ou
make migrate-create msg="Description"

# Appliquer les migrations
alembic upgrade head
# ou
make migrate

# Annuler la dernière migration
alembic downgrade -1
# ou
make migrate-down
```

## 📊 Modèles de données

### Customer (Client)

- Types : Particulier, Professionnel, Distributeur, Admin
- Statuts : Actif, Inactif, Suspendu, En attente
- Informations personnelles et professionnelles
- Authentification intégrée

### Address (Adresse)

- Types : Livraison, Facturation, Livraison/Facturation
- Support multi-adresses
- Adresse par défaut

### UserAuth

- Gestion des tokens de rafraîchissement
- Historique des sessions

## 🔐 Sécurité

- Mots de passe hashés avec bcrypt
- Authentification JWT
- Tokens d'accès (30 min) et de rafraîchissement (7 jours)
- Permissions basées sur les rôles
- Validation des données avec Pydantic

## 🌐 Intégration RabbitMQ

### Événements publiés

- `customer.created` - Client créé
- `customer.updated` - Client mis à jour
- `customer.deleted` - Client supprimé
- `customer.status_changed` - Statut modifié
- `address.created` - Adresse créée
- `address.updated` - Adresse mise à jour
- `address.deleted` - Adresse supprimée

### Événements consommés

- `order.created` - Commande créée (depuis service Commandes)
- `product.reserved` - Produit réservé (depuis service Produits)

## 📝 Variables d'environnement

Voir `.env.template` pour la liste complète. Principales variables :

```env
DATABASE_URL=postgresql://...
RABBITMQ_HOST=localhost
SECRET_KEY=your-secret-key
DEBUG=True
```

## 🐳 Docker

```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Logs
docker-compose logs -f

# Stop
docker-compose down

# Tests
docker-compose -f docker-compose.test.yml up
```

## 📖 Documentation API

La documentation complète de l'API est disponible via :

- Swagger UI : `/docs`
- ReDoc : `/redoc`
- OpenAPI JSON : `/openapi.json`

## 🤝 Contribution

1. Créer une branche feature : `git checkout -b feature/ma-feature`
2. Commit : `git commit -m 'Ajout de ma feature'`
3. Push : `git push origin feature/ma-feature`
4. Créer une Pull Request

## 📄 Licence

Propriété de PayeTonKawa - Tous droits réservés

## 👥 Équipe

Équipe de 4 développeurs - Projet MSPR4

## 📞 Support

Pour toute question ou problème, veuillez ouvrir une issue sur GitHub.

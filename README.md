# PayeTonKawa - Service Clients ☕

## 🎯 Vue d'ensemble

Bienvenue dans le repository du **Service Clients** de PayeTonKawa, l'importateur de café en France.

Ce repository contient un microservice complet et production-ready pour la gestion des clients (particuliers et professionnels).

## 📦 Contenu du Repository

### `api-clients/` - Service Clients Principal

Microservice FastAPI pour la gestion des clients, adresses et authentification.

**Stack Technique:**
- Python 3.11 + FastAPI
- PostgreSQL 15
- RabbitMQ 3
- Docker & Docker Compose

**Features:**
- ✅ Gestion clients (particuliers/professionnels)
- ✅ Gestion adresses (livraison/facturation)
- ✅ Authentification JWT
- ✅ Permissions par rôles
- ✅ Événements RabbitMQ
- ✅ Tests automatisés
- ✅ CI/CD GitHub Actions

## 🚀 Démarrage rapide

```bash
cd api-clients

# Avec Docker (recommandé)
docker-compose up -d
docker-compose exec api alembic upgrade head
docker-compose exec api python scripts/seed_data.py

# API disponible sur http://localhost:8000
# Documentation: http://localhost:8000/docs
```

## 📚 Documentation

- **[README Principal](api-clients/README.md)** - Guide complet du service
- **[Quick Start](api-clients/docs/QUICKSTART.md)** - Démarrage en 5 minutes
- **[Architecture](api-clients/docs/architecture/ARCHITECTURE.md)** - Architecture détaillée
- **[API Reference](api-clients/docs/api/API_REFERENCE.md)** - Documentation API complète
- **[Deployment](api-clients/docs/deployment/DEPLOYMENT.md)** - Guide de déploiement
- **[Project Summary](api-clients/PROJECT_SUMMARY.md)** - Résumé du projet

## 🔑 Comptes de test

Après avoir exécuté `seed_data.py` :

```
Admin:
  Email: admin@payetonkawa.fr
  Password: admin123

Client particulier:
  Email: marie.dupont@example.com
  Password: password123

Client professionnel:
  Email: contact@cafepro.fr
  Password: password123
```

## 🏗️ Architecture

```
Service Clients (FastAPI)
    ↓
PostgreSQL (Données clients)
    ↓
RabbitMQ (Communication inter-services)
    ↓
Services Produits & Commandes (à venir)
```

## 📊 Statistiques

- **72 fichiers** créés
- **54 fichiers Python**
- **18 endpoints REST**
- **5 guides** de documentation
- **Test suite** complète
- **Production ready** ✅

## 🧪 Tests

```bash
cd api-clients
make test           # Tous les tests
make test-cov       # Avec couverture
```

## 📡 API Endpoints

### Authentification
- `POST /api/v1/auth/login` - Connexion
- `POST /api/v1/auth/refresh` - Rafraîchir token
- `POST /api/v1/auth/change-password` - Changer mot de passe

### Clients
- `POST /api/v1/customers/` - Créer client
- `GET /api/v1/customers/me` - Mon profil
- `PUT /api/v1/customers/{id}` - Modifier client
- `GET /api/v1/customers/` - Liste clients (admin)

### Adresses
- `POST /api/v1/addresses/` - Créer adresse
- `GET /api/v1/addresses/` - Mes adresses
- `PUT /api/v1/addresses/{id}` - Modifier adresse

### Administration
- `POST /api/v1/admin/customers/{id}/activate` - Activer
- `POST /api/v1/admin/customers/{id}/suspend` - Suspendre
- `GET /api/v1/admin/stats` - Statistiques

## 🔧 Développement

```bash
cd api-clients

# Installation
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Lancer en dev
make run

# Formater le code
make format

# Linter
make lint
```

## 🚢 Déploiement

```bash
cd api-clients

# Production avec Docker
docker-compose -f docker-compose.prod.yml up -d

# Voir le guide complet: docs/deployment/DEPLOYMENT.md
```

## 🤝 Contribution

1. Créer une branche feature
2. Développer et tester
3. Soumettre une Pull Request
4. Review et merge

## 📄 Licence

Propriété de PayeTonKawa - Tous droits réservés

## 👥 Équipe

Projet MSPR4 - Équipe de développement PayeTonKawa

## 📞 Support

Pour toute question:
- Consulter la documentation dans `api-clients/docs/`
- Ouvrir une issue sur GitHub
- Contacter l'équipe de développement

---

**Status:** ✅ Production Ready
**Version:** 1.0.0
**Last Update:** Décembre 2024

🚀 **Le Service Clients est prêt pour la production!** ☕

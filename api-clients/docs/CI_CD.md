# CI/CD Pipeline Documentation - Service Clients PayeTonKawa

## 🎯 Vue d'ensemble

Le pipeline CI/CD pour le Service Clients est configuré pour assurer la qualité du code, la sécurité et la fiabilité à chaque modification.

## 🔄 Déclencheurs

Le pipeline se déclenche automatiquement sur :

### Branches surveillées :
- `main` - Production
- `develop` - Développement
- `feature/**` - Nouvelles fonctionnalités
- `release/**` - Préparation de releases

### Événements :
- **Push** - À chaque commit poussé sur les branches surveillées
- **Pull Request** - À chaque PR vers les branches surveillées

## 📋 Étapes du Pipeline

### 1️⃣ Lint (Analyse de code)

**Durée estimée :** 2-3 minutes

Analyse la qualité et le style du code pour détecter :
- Erreurs de syntaxe critiques
- Problèmes de complexité cyclomatique (max 10)
- Respect des conventions de style Python (PEP 8)
- Cohérence du formatage (Black, isort)
- Vérification des types (MyPy)

**Outils utilisés :**
- `flake8` - Linter Python
- `black` - Formateur de code
- `isort` - Tri des imports
- `mypy` - Vérification de types statique

**Commande locale :**
```bash
cd api-clients
flake8 app tests
black --check app tests
isort --check-only app tests
mypy app --ignore-missing-imports
```

### 2️⃣ Tests (Tests unitaires et couverture)

**Durée estimée :** 3-5 minutes

Exécute la suite de tests avec :
- Tests unitaires de tous les services
- Tests d'intégration
- Tests des endpoints API
- **Couverture minimale requise : 40%**

**Services de test :**
- PostgreSQL 15 (port 5433)
- RabbitMQ 3 (port 5673)

**Outils utilisés :**
- `pytest` - Framework de test
- `pytest-cov` - Mesure de couverture
- `pytest-asyncio` - Support des tests async

**Commande locale :**
```bash
cd api-clients
docker-compose -f docker-compose.test.yml up -d
sleep 5
pytest tests/ -v --cov=app --cov-report=term --cov-fail-under=40
docker-compose -f docker-compose.test.yml down
```

**Artefacts générés :**
- Rapport de couverture XML (pour Codecov)
- Rapport de couverture HTML (téléchargeable pendant 30 jours)

### 3️⃣ Security (Analyse de sécurité)

**Durée estimée :** 3-4 minutes

Effectue plusieurs analyses de sécurité :

#### a) pip-audit - Vulnérabilités des dépendances
Vérifie si les packages Python ont des vulnérabilités connues dans la base de données PyPI Advisory.

```bash
pip-audit --desc
```

#### b) Bandit - Analyse statique de sécurité
Détecte les problèmes de sécurité courants dans le code Python :
- Injections SQL
- Désérialisation non sécurisée
- Problèmes de cryptographie
- Gestion des mots de passe

```bash
bandit -r app -f screen
```

#### c) OWASP Dependency-Check
Analyse les dépendances pour les vulnérabilités CVE connues.

**Artefacts générés :**
- Rapport pip-audit JSON (30 jours)
- Rapport Bandit JSON (30 jours)
- Rapport OWASP HTML (30 jours)

### 4️⃣ Build (Compilation et vérification)

**Durée estimée :** 4-6 minutes

Vérifie que l'application peut être construite et déployée :

1. **Vérification Python**
   - Installation des dépendances
   - Import de l'application
   - Vérification de la structure

2. **Build Docker**
   - Construction de l'image Docker
   - Test de l'image
   - Tag avec le SHA du commit

3. **Sauvegarde de l'image** (uniquement pour `main` et `develop`)
   - Compression de l'image Docker
   - Upload en tant qu'artefact (7 jours)

**Commande locale :**
```bash
cd api-clients
docker build -t payetonkawa-api-clients:latest .
docker run --rm payetonkawa-api-clients:latest python -c "import app; print('OK')"
```

### 5️⃣ Summary (Résumé)

Génère un résumé complet du pipeline avec :
- Statut de chaque job
- Branche et commit
- Résultat global (✅ succès / ❌ échec)

## 📊 Métriques et Seuils

| Métrique | Seuil | Description |
|----------|-------|-------------|
| Couverture de code | ≥ 40% | Minimum requis pour passer |
| Complexité cyclomatique | ≤ 10 | Maximum par fonction |
| Longueur de ligne | ≤ 127 | Maximum de caractères |
| Vulnérabilités critiques | 0 | Bloquant si détecté |

## 🔧 Configuration locale

### Prérequis
```bash
cd api-clients
pip install -r requirements-dev.txt
pip install -r requirements-test.txt
```

### Lancer tous les checks localement
```bash
# Lint
flake8 app tests
black --check app tests
isort --check-only app tests

# Tests
docker-compose -f docker-compose.test.yml up -d
sleep 5
pytest tests/ -v --cov=app --cov-report=term --cov-fail-under=40
docker-compose -f docker-compose.test.yml down

# Sécurité
safety check
bandit -r app

# Build
docker build -t payetonkawa-api-clients:test .
```

### Auto-formatage du code
```bash
black app tests
isort app tests
```

## 🚀 Déploiement

Le pipeline **ne déploie pas automatiquement**. Les artefacts sont disponibles pour un déploiement manuel ou via un pipeline CD séparé.

### Artefacts disponibles :
1. **Image Docker** (main/develop, 7 jours)
2. **Rapport de couverture** (30 jours)
3. **Rapports de sécurité** (30 jours)

## 🔍 Débogage des échecs

### Échec du Lint
```bash
# Voir les erreurs
flake8 app tests

# Auto-corriger
black app tests
isort app tests
```

### Échec des Tests
```bash
# Lancer avec verbose
pytest tests/ -vv

# Lancer un test spécifique
pytest tests/test_customers.py::test_create_customer -vv

# Voir la couverture
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### Échec de la Sécurité
```bash
# Voir les vulnérabilités détaillées
safety check --full-report
bandit -r app -v

# Mettre à jour les dépendances
pip list --outdated
```

### Échec du Build
```bash
# Tester l'import
python -c "import app"

# Vérifier les dépendances
pip check

# Rebuilder l'image
docker build -t test . --no-cache
```

## 📝 Bonnes pratiques

1. **Avant de pousser :**
   - Exécuter le lint localement
   - Lancer les tests
   - Vérifier la couverture

2. **Pull Requests :**
   - Attendre que tous les checks passent
   - Résoudre tous les problèmes de sécurité
   - Maintenir la couverture > 40%

3. **Commits :**
   - Messages descriptifs
   - Petits commits atomiques
   - Tests ajoutés pour le nouveau code

## 🔗 Ressources

- [Workflow GitHub](.github/workflows/ci-api-clients.yml)
- [Configuration Pytest](pytest.ini)
- [Configuration Flake8](.flake8)
- [Configuration Black/isort/Bandit](pyproject.toml)
- [Documentation API](docs/API_REFERENCE.md)

## 📧 Support

En cas de problème avec le pipeline CI/CD, vérifiez :
1. Les logs du job en échec sur GitHub Actions
2. La documentation ci-dessus
3. Les issues GitHub du projet

---

**Version :** 1.0.0  
**Dernière mise à jour :** 2026-01-03  
**Pipeline :** GitHub Actions

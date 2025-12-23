# Architecture du Service Clients

## 🏗️ Vue d'ensemble

Le Service Clients est un microservice autonome qui gère toutes les opérations liées aux clients de PayeTonKawa.

```
┌─────────────────────────────────────────────────────────────┐
│                    Service Clients (API)                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   FastAPI    │  │  Security    │  │   Events     │      │
│  │   Endpoints  │→ │     JWT      │  │  RabbitMQ    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         ↓                                     ↑              │
│  ┌──────────────────────────────────────────┐│              │
│  │         Services (Business Logic)        ││              │
│  │  - CustomerService                       ││              │
│  │  - AddressService                        ││              │
│  │  - AuthService                           ││              │
│  │  - EventService                          ││              │
│  └──────────────────────────────────────────┘│              │
│         ↓                                     │              │
│  ┌──────────────────────────────────────────┐│              │
│  │      Repositories (Data Access)          ││              │
│  │  - CustomerRepository                    ││              │
│  │  - AddressRepository                     ││              │
│  └──────────────────────────────────────────┘│              │
│         ↓                                     │              │
│  ┌──────────────────────────────────────────┐│              │
│  │         Models (SQLAlchemy)              ││              │
│  │  - Customer                              ││              │
│  │  - Address                               ││              │
│  │  - UserAuth                              ││              │
│  └──────────────────────────────────────────┘│              │
│         ↓                                     │              │
└─────────┼─────────────────────────────────────┼──────────────┘
          ↓                                     ↓
    ┌──────────┐                         ┌──────────┐
    │PostgreSQL│                         │ RabbitMQ │
    └──────────┘                         └──────────┘
```

## 📊 Modèle de données

### Customer (Client)

```
customers
├── id (UUID, PK)
├── reference (String, Unique)
├── civilite (String)
├── nom (String)
├── prenom (String)
├── email (String, Unique)
├── telephone (String)
├── mobile (String)
├── type_client (Enum)
├── statut (Enum)
├── raison_sociale (String, nullable)
├── siret (String, nullable, unique)
├── tva_intracommunautaire (String, nullable)
├── nom_contact (String, nullable)
├── hashed_password (String)
├── email_confirme (Boolean)
├── date_derniere_connexion (DateTime)
├── preferences (Text)
├── date_creation (DateTime)
├── date_modification (DateTime)
└── date_desactivation (DateTime, nullable)
```

### Address (Adresse)

```
addresses
├── id (UUID, PK)
├── client_id (UUID, FK → customers.id)
├── type_adresse (Enum)
├── est_defaut (Boolean)
├── libelle (String)
├── destinataire (String)
├── adresse_ligne1 (String)
├── adresse_ligne2 (String, nullable)
├── code_postal (String)
├── ville (String)
├── pays (String)
├── instructions_livraison (String, nullable)
├── telephone (String, nullable)
├── date_creation (DateTime)
└── date_modification (DateTime)
```

### UserAuth (Sessions)

```
user_auth
├── id (UUID, PK)
├── customer_id (UUID, FK → customers.id)
├── refresh_token (String, Unique)
├── token_expiry (DateTime)
├── device_info (String, nullable)
├── ip_address (String, nullable)
├── user_agent (String, nullable)
├── date_creation (DateTime)
└── date_derniere_utilisation (DateTime)
```

## 🔄 Flux de données

### 1. Création de compte

```
Client → POST /api/v1/customers/
    ↓
CustomerService.create_customer()
    ↓
- Valider les données (Pydantic)
- Vérifier unicité email/SIRET
- Hasher le mot de passe
- Générer référence unique
    ↓
CustomerRepository.create()
    ↓
Base de données PostgreSQL
    ↓
EventService.create_customer_event()
    ↓
RabbitMQ (customer.created)
    ↓
← Retour CustomerResponse
```

### 2. Authentification

```
Client → POST /api/v1/auth/login
    ↓
AuthService.authenticate()
    ↓
- Vérifier email existe
- Vérifier mot de passe
- Vérifier statut actif
- Créer access_token (JWT)
- Créer refresh_token (JWT)
- Sauvegarder refresh_token
    ↓
← Retour tokens + expires_in
```

### 3. Accès protégé

```
Client → GET /api/v1/customers/me
    ↓
Headers: Authorization: Bearer <token>
    ↓
get_current_user() (Dependency)
    ↓
- Extraire token du header
- Décoder JWT
- Vérifier signature
- Vérifier expiration
- Récupérer customer_id
    ↓
CustomerRepository.get_by_id()
    ↓
← Retour Customer
```

## 🎯 Patterns architecturaux

### 1. Repository Pattern

Abstraction de l'accès aux données :

```python
# Repository : Accès données uniquement
class CustomerRepository:
    async def get_by_id(id: str) -> Customer
    async def get_by_email(email: str) -> Customer
    async def create(customer: Customer) -> Customer
    # ...

# Service : Logique métier
class CustomerService:
    async def create_customer(data: CustomerCreate):
        # Validation métier
        # Transformation
        # Appel repository
        # Événements
```

### 2. Dependency Injection

Utilisation des dépendances FastAPI :

```python
@router.get("/me")
async def get_me(
    current_user: Customer = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # current_user est injecté automatiquement
    # après vérification du token JWT
```

### 3. Event-Driven Architecture

Communication asynchrone via RabbitMQ :

```python
# Publication d'événement
event = EventService.create_customer_event(...)
await event_producer.publish_customer_event(event)

# Consommation d'événement
await event_consumer.consume(
    queue_name="orders-queue",
    routing_keys=["order.created"],
    callback=handle_order_created
)
```

## 🔒 Sécurité

### 1. Authentification JWT

```
Access Token (30 min)
- Utilisé pour chaque requête
- Contenu : {sub: customer_id, exp: timestamp}
- Stocké côté client (localStorage/cookie)

Refresh Token (7 jours)
- Utilisé pour renouveler access_token
- Stocké en base de données
- Peut être révoqué
```

### 2. Hash des mots de passe

```python
# Utilisation de bcrypt via passlib
pwd_context = CryptContext(schemes=["bcrypt"])
hashed = pwd_context.hash(password)
verified = pwd_context.verify(plain, hashed)
```

### 3. Permissions basées sur les rôles

```python
ROLE_PERMISSIONS = {
    CustomerType.PARTICULIER: [READ, WRITE],
    CustomerType.ADMIN: [READ, WRITE, DELETE, ADMIN]
}
```

## 🚀 Scalabilité

### 1. Asynchrone

- FastAPI avec async/await
- SQLAlchemy avec AsyncPG
- Sessions de base de données asynchrones

### 2. Stateless

- Pas de session côté serveur
- JWT auto-contenu
- Permet scaling horizontal

### 3. Cache (Future)

```python
# Redis pour cache
- Cache des requêtes fréquentes
- Cache des tokens
- Rate limiting
```

### 4. Load Balancing (Future)

```
     ┌────────────┐
     │   Nginx    │
     └─────┬──────┘
           │
     ┌─────┴──────┐
     │            │
┌────▼───┐   ┌───▼────┐
│ API #1 │   │ API #2 │
└────┬───┘   └───┬────┘
     │           │
     └─────┬─────┘
           │
      ┌────▼────┐
      │  DB RO  │
      └─────────┘
```

## 🔍 Monitoring (Future)

### Métriques à surveiller

1. **Performance**
   - Temps de réponse API
   - Latence base de données
   - Taux d'erreur

2. **Business**
   - Nombre de créations/jour
   - Taux de confirmation email
   - Taux de connexion

3. **Infrastructure**
   - CPU/RAM utilisation
   - Connexions DB actives
   - Files RabbitMQ

## 🔄 CI/CD

```
GitHub Push → GitHub Actions
    ↓
1. Tests unitaires
2. Tests d'intégration
3. Linting & Format
4. Build Docker
    ↓
Deploy (Production)
    ↓
1. Pull image Docker
2. Run migrations
3. Deploy new version
4. Health check
```

## 📚 Évolutions futures

1. **Cache Redis** : Performance
2. **ElasticSearch** : Recherche avancée
3. **Monitoring** : Prometheus + Grafana
4. **Rate Limiting** : Protection API
5. **API Versioning** : v2, v3...
6. **GraphQL** : Alternative REST
7. **WebSockets** : Notifications temps réel

# API Reference - Service Clients

## 📚 Documentation complète de l'API

Base URL: `https://api.payetonkawa.fr/api/v1`

## 🔐 Authentification

L'API utilise JWT Bearer Token pour l'authentification.

```
Authorization: Bearer <access_token>
```

## 📋 Endpoints

### Authentication

#### POST /auth/login

Authentifier un utilisateur et obtenir les tokens.

**Request:**
```json
{
  "email": "marie.dupont@example.com",
  "password": "password123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Errors:**
- `401 Unauthorized` - Email ou mot de passe incorrect
- `403 Forbidden` - Compte non actif

#### POST /auth/refresh

Rafraîchir un access token expiré.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### POST /auth/change-password

Changer le mot de passe de l'utilisateur connecté.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "old_password": "password123",
  "new_password": "newpassword123"
}
```

**Response:** `204 No Content`

**Errors:**
- `401 Unauthorized` - Ancien mot de passe incorrect

#### POST /auth/confirm-email

Confirmer l'adresse email avec le token reçu.

**Request:**
```json
{
  "token": "email_confirmation_token"
}
```

**Response:** `200 OK`
```json
{
  "message": "Email confirmed successfully",
  "email": "marie.dupont@example.com"
}
```

---

### Customers

#### POST /customers/

Créer un nouveau compte client.

**Request:**
```json
{
  "civilite": "Mme",
  "nom": "Dupont",
  "prenom": "Marie",
  "email": "marie.dupont@example.com",
  "telephone": "0612345678",
  "mobile": "0698765432",
  "type_client": "particulier",
  "password": "password123"
}
```

Pour un client professionnel :
```json
{
  "civilite": "M",
  "nom": "Martin",
  "prenom": "Jean",
  "email": "contact@cafepro.fr",
  "telephone": "0145678901",
  "type_client": "professionnel",
  "raison_sociale": "Café Pro SARL",
  "siret": "12345678901234",
  "tva_intracommunautaire": "FR12345678901",
  "nom_contact": "Jean Martin",
  "password": "password123"
}
```

**Response:** `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "reference": "CLI20240123ABC123",
  "civilite": "Mme",
  "nom": "Dupont",
  "prenom": "Marie",
  "email": "marie.dupont@example.com",
  "telephone": "0612345678",
  "mobile": "0698765432",
  "type_client": "particulier",
  "statut": "en_attente",
  "email_confirme": false,
  "date_creation": "2024-01-23T10:30:00Z",
  "date_modification": "2024-01-23T10:30:00Z"
}
```

**Errors:**
- `400 Bad Request` - Email ou SIRET déjà utilisé
- `422 Unprocessable Entity` - Données invalides

#### GET /customers/me

Obtenir les informations du client connecté avec ses adresses.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "reference": "CLI20240123ABC123",
  "civilite": "Mme",
  "nom": "Dupont",
  "prenom": "Marie",
  "email": "marie.dupont@example.com",
  "telephone": "0612345678",
  "type_client": "particulier",
  "statut": "actif",
  "email_confirme": true,
  "date_derniere_connexion": "2024-01-23T15:00:00Z",
  "date_creation": "2024-01-23T10:30:00Z",
  "date_modification": "2024-01-23T10:30:00Z",
  "adresses": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "type_adresse": "livraison_facturation",
      "est_defaut": true,
      "libelle": "Domicile",
      "destinataire": "Marie Dupont",
      "adresse_ligne1": "123 Rue de la Paix",
      "code_postal": "75001",
      "ville": "Paris",
      "pays": "France",
      "date_creation": "2024-01-23T11:00:00Z"
    }
  ]
}
```

#### GET /customers/{customer_id}

Obtenir un client par son ID (admin ou propriétaire uniquement).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "reference": "CLI20240123ABC123",
  ...
}
```

**Errors:**
- `403 Forbidden` - Pas les permissions nécessaires
- `404 Not Found` - Client non trouvé

#### PUT /customers/{customer_id}

Mettre à jour un client (admin ou propriétaire uniquement).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "telephone": "0687654321",
  "mobile": "0612349876",
  "preferences": "{\"newsletter\": true}"
}
```

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "telephone": "0687654321",
  ...
}
```

#### DELETE /customers/{customer_id}

Supprimer un client (admin uniquement).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `204 No Content`

**Errors:**
- `403 Forbidden` - Nécessite droits admin
- `404 Not Found` - Client non trouvé

#### GET /customers/?skip=0&limit=100&search=dupont

Lister tous les clients avec pagination et recherche (admin uniquement).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (int, optional): Nombre d'éléments à sauter (default: 0)
- `limit` (int, optional): Nombre d'éléments par page (default: 100, max: 100)
- `search` (string, optional): Terme de recherche

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "reference": "CLI20240123ABC123",
      ...
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 100,
  "pages": 2
}
```

---

### Addresses

#### POST /addresses/

Créer une nouvelle adresse pour le client connecté.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "type_adresse": "livraison",
  "est_defaut": true,
  "libelle": "Bureau",
  "destinataire": "Marie Dupont",
  "adresse_ligne1": "10 Avenue des Champs-Élysées",
  "adresse_ligne2": "Batiment B, 3ème étage",
  "code_postal": "75008",
  "ville": "Paris",
  "pays": "France",
  "instructions_livraison": "Sonner au bureau",
  "telephone": "0123456789"
}
```

**Response:** `201 Created`
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "client_id": "550e8400-e29b-41d4-a716-446655440000",
  "type_adresse": "livraison",
  "est_defaut": true,
  "libelle": "Bureau",
  "adresse_ligne1": "10 Avenue des Champs-Élysées",
  "adresse_ligne2": "Batiment B, 3ème étage",
  "code_postal": "75008",
  "ville": "Paris",
  "pays": "France",
  "date_creation": "2024-01-23T11:00:00Z",
  "date_modification": "2024-01-23T11:00:00Z"
}
```

#### GET /addresses/

Lister toutes les adresses du client connecté.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "type_adresse": "livraison",
    "est_defaut": true,
    "libelle": "Domicile",
    ...
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440002",
    "type_adresse": "facturation",
    "est_defaut": false,
    "libelle": "Bureau",
    ...
  }
]
```

#### GET /addresses/default

Obtenir l'adresse par défaut du client connecté.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "est_defaut": true,
  ...
}
```

**Errors:**
- `404 Not Found` - Aucune adresse par défaut

#### GET /addresses/{address_id}

Obtenir une adresse spécifique.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  ...
}
```

**Errors:**
- `403 Forbidden` - Adresse n'appartient pas au client
- `404 Not Found` - Adresse non trouvée

#### PUT /addresses/{address_id}

Mettre à jour une adresse.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "telephone": "0198765432",
  "instructions_livraison": "Laisser au gardien si absent"
}
```

**Response:** `200 OK`
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "telephone": "0198765432",
  "instructions_livraison": "Laisser au gardien si absent",
  ...
}
```

#### DELETE /addresses/{address_id}

Supprimer une adresse.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `204 No Content`

#### POST /addresses/{address_id}/set-default

Définir une adresse comme adresse par défaut.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "est_defaut": true,
  ...
}
```

---

### Admin

#### POST /admin/customers/{customer_id}/activate

Activer un compte client (admin uniquement).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "statut": "actif",
  ...
}
```

#### POST /admin/customers/{customer_id}/suspend

Suspendre un compte client (admin uniquement).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "statut": "suspendu",
  ...
}
```

#### GET /admin/stats

Obtenir les statistiques des clients (admin uniquement).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "total_customers": 1250,
  "by_type": {
    "particulier": 1000,
    "professionnel": 200,
    "distributeur": 45,
    "admin": 5
  },
  "by_status": {
    "actif": 1100,
    "inactif": 50,
    "suspendu": 25,
    "en_attente": 75
  }
}
```

---

## 🔢 Codes d'erreur

| Code | Description |
|------|-------------|
| 200 | OK - Requête réussie |
| 201 | Created - Ressource créée |
| 204 | No Content - Succès sans contenu |
| 400 | Bad Request - Données invalides |
| 401 | Unauthorized - Non authentifié |
| 403 | Forbidden - Pas les permissions |
| 404 | Not Found - Ressource non trouvée |
| 422 | Unprocessable Entity - Validation échouée |
| 500 | Internal Server Error - Erreur serveur |

## 📊 Types et Enums

### CustomerType
- `particulier` - Client particulier
- `professionnel` - Client professionnel
- `distributeur` - Distributeur
- `admin` - Administrateur

### CustomerStatus
- `actif` - Compte actif
- `inactif` - Compte inactif
- `suspendu` - Compte suspendu
- `en_attente` - En attente de confirmation

### AddressType
- `livraison` - Adresse de livraison
- `facturation` - Adresse de facturation
- `livraison_facturation` - Les deux

## 🧪 Exemples avec cURL

### Créer un compte et se connecter

```bash
# 1. Créer un compte
curl -X POST http://localhost:8000/api/v1/customers/ \
  -H "Content-Type: application/json" \
  -d '{
    "civilite": "M",
    "nom": "Test",
    "prenom": "User",
    "email": "test@example.com",
    "type_client": "particulier",
    "password": "password123"
  }'

# 2. Se connecter
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# 3. Utiliser le token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET http://localhost:8000/api/v1/customers/me \
  -H "Authorization: Bearer $TOKEN"
```

## 📝 Notes

- Les tokens expirent après 30 minutes
- Tous les timestamps sont en UTC
- Les UUIDs sont au format UUID4
- Les montants sont en euros
- Les numéros de téléphone sont au format français

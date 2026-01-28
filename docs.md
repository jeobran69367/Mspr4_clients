# 5.1 Sécurité des APIs

La sécurité des APIs est un pilier essentiel pour garantir la confidentialité, l'intégrité et la disponibilité des données et des services. Dans ce projet, des mécanismes de sécurité avancés ont été mis en œuvre pour protéger l'API contre les menaces courantes et respecter les standards de sécurité de l'industrie.

---

## 5.1.1 Authentification et Autorisation

### Authentification via JWT (JSON Web Tokens)
- **Principe** : L'API implémente une authentification basée sur des tokens JWT. Ces tokens sont générés lors de la connexion et contiennent des informations signées permettant de vérifier l'identité de l'utilisateur sans requêtes supplémentaires à la base de données.
- **Caractéristiques techniques** :
  - **Algorithmes de signature** : Utilisation de HS256 (clé secrète) ou RS256 (clé publique/privée) pour garantir l'intégrité et l'authenticité des tokens.
  - **Expiration des tokens** : Les tokens incluent un champ `exp` pour limiter leur durée de validité. Une durée courte est recommandée pour les tokens d'accès, complétée par des tokens de rafraîchissement.
  - **Revocation** : Implémentation d'une liste noire (blacklist) pour invalider les tokens compromis ou révoqués.
- **Recommandations** :
  - Stocker les tokens côté client dans des cookies sécurisés (`HttpOnly`, `Secure`, `SameSite=Strict`) pour réduire les risques d'attaques XSS.
  - Ne pas inclure d'informations sensibles dans le payload des tokens JWT.

### Autorisation basée sur les rôles et permissions
- **Rôles et permissions** :
  - Les utilisateurs sont associés à des rôles (ex. : `admin`, `user`) définis dans la base de données.
  - Les permissions sont gérées via des middlewares qui vérifient les rôles avant d'autoriser l'accès aux endpoints.
- **Mise en œuvre** :
  - Les middlewares analysent les claims des tokens JWT pour déterminer les permissions.
  - Les actions sensibles (ex. : suppression de données) sont strictement limitées aux utilisateurs autorisés.

---

## 5.1.2 Chiffrement des Échanges

### Utilisation de HTTPS
- **Principe** : Toutes les communications entre les clients et l'API sont chiffrées via HTTPS pour protéger les données en transit.
- **Mise en œuvre** :
  - Un certificat SSL/TLS valide est configuré pour les environnements de production.
  - Les connexions HTTP sont redirigées automatiquement vers HTTPS.
- **Recommandations** :
  - Utiliser des certificats émis par des autorités de certification reconnues (ex. : Let's Encrypt, DigiCert).
  - Activer les protocoles TLS 1.2 ou TLS 1.3 uniquement.

### Chiffrement des données sensibles
- **Mots de passe** :
  - Les mots de passe des utilisateurs sont hachés avec l'algorithme bcrypt (coût de calcul : 12 ou supérieur).
  - Les mots de passe ne sont jamais stockés en clair.
- **Données sensibles** :
  - Les informations sensibles (ex. : clés API, tokens JWT) sont chiffrées avant d'être stockées.
  - Les variables d'environnement contenant des secrets sont gérées via des outils comme **Docker Secrets** ou **Azure Key Vault**.

---

## 5.1.3 Contrôle des Usages

### Limitation du taux de requêtes (Rate Limiting)
- **Objectif** : Prévenir les abus et les attaques par déni de service (DoS).
- **Mise en œuvre** :
  - Utilisation d'un middleware de limitation de taux (ex. : `fastapi-limiter`) basé sur Redis.
  - Configuration des limites par utilisateur/IP (ex. : 100 requêtes par minute).
- **Recommandations** :
  - Bloquer temporairement les adresses IP après plusieurs violations des limites.

### Validation des entrées utilisateur
- **Objectif** : Prévenir les attaques par injection (SQL, XSS, etc.).
- **Mise en œuvre** :
  - Validation stricte des données entrantes avec Pydantic (FastAPI).
  - Rejet des données non conformes aux schémas définis.
- **Exemple** :
  ```python
  from pydantic import BaseModel, EmailStr

  class UserInput(BaseModel):
      username: str
      email: EmailStr
      age: int
  ```

### Journalisation et surveillance
- **Objectif** : Détecter les comportements anormaux et les tentatives d'intrusion.
- **Mise en œuvre** :
  - Centralisation des logs avec des outils comme ELK Stack (Elasticsearch, Logstash, Kibana).
  - Surveillance des métriques système (CPU, mémoire) et des logs applicatifs.

---

## 5.1.4 Protection contre les Menaces Courantes

### Protection contre les attaques CSRF (Cross-Site Request Forgery)
- **Principe** : Les endpoints sensibles sont protégés contre les attaques CSRF.
- **Mise en œuvre** :
  - Utilisation de tokens anti-CSRF générés côté serveur et vérifiés pour chaque requête POST, PUT ou DELETE.

### Protection contre les attaques par force brute
- **Principe** : Limiter les tentatives de connexion répétées avec des identifiants incorrects.
- **Mise en œuvre** :
  - Verrouillage temporaire des comptes après plusieurs échecs consécutifs.
  - Surveillance des adresses IP suspectes.

### Protection contre les vulnérabilités OWASP Top 10
- **Injection SQL** : Utilisation de requêtes paramétrées pour éviter les injections SQL.
- **Exposition de données sensibles** : Masquage des informations sensibles dans les réponses de l'API.
- **Mauvaise configuration de sécurité** : Remplacement des identifiants par défaut (ex. : `guest` pour RabbitMQ).

---

## 5.1.5 Bonnes Pratiques Supplémentaires

- **Rotation des clés JWT** :
  - Les clés de signature des tokens JWT sont renouvelées périodiquement.
- **Séparation des environnements** :
  - Les environnements de développement, de test et de production sont isolés.
  - Les configurations sensibles sont externalisées dans des fichiers `.env` ou des gestionnaires de secrets.
- **Mises à jour régulières** :
  - Les dépendances et les images Docker (PostgreSQL, RabbitMQ) sont mises à jour pour inclure les derniers correctifs de sécurité.

---

## 5.1.6 Plan de Réponse aux Incidents

1. **Détection** : Surveillance en temps réel des journaux pour identifier les activités suspectes.
2. **Analyse** : Évaluation de l'impact et identification de la source de l'incident.
3. **Notification** : Les parties prenantes concernées sont informées rapidement.
4. **Correction** : Les vulnérabilités sont corrigées et les systèmes compromis sont restaurés.
5. **Prévention** : Des mesures supplémentaires sont mises en place pour éviter des incidents similaires.

---

Cette documentation technique fournit une vue d'ensemble détaillée des mesures de sécurité mises en œuvre pour l'API. Elle est conforme aux meilleures pratiques de l'industrie et peut être adaptée en fonction des exigences spécifiques du projet.
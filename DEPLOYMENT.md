# 🚀 Guide de Déploiement - Vercel & Render

Ce guide vous explique comment déployer votre application SQL to NoSQL Converter sur Vercel (frontend) et Render (backend).

---

## 📋 Table des Matières

1. [Prérequis](#prérequis)
2. [Déploiement Backend (Render)](#déploiement-backend-render)
3. [Déploiement Frontend (Vercel)](#déploiement-frontend-vercel)
4. [Configuration Post-Déploiement](#configuration-post-déploiement)
5. [Vérification](#vérification)
6. [Dépannage](#dépannage)

---

## Prérequis

### Comptes Nécessaires
- ✅ Compte GitHub (pour le code source)
- ✅ Compte Render (https://render.com) - Gratuit
- ✅ Compte Vercel (https://vercel.com) - Gratuit
- ✅ Clé API BlazeAPI (pour l'IA)

### Préparation du Code
```bash
# 1. Créer un repository GitHub
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/votre-username/sql-nosql-converter.git
git push -u origin main
```

---

## Déploiement Backend (Render)

### Étape 1 : Créer le fichier `render.yaml`

Créez `render.yaml` à la racine du projet :

```yaml
services:
  - type: web
    name: sql-nosql-backend
    env: python
    region: frankfurt  # ou oregon, singapore
    plan: free
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.13.0
      - key: AI_PROVIDER
        value: blazeapi
      - key: BLAZEAPI_API_KEY
        sync: false  # À configurer manuellement
      - key: BLAZEAPI_BASE_URL
        value: https://blazeai.boxu.dev/api/
      - key: BLAZEAPI_MODEL
        value: claude-opus-4-7
      - key: OLLAMA_BASE_URL
        value: http://localhost:11434
      - key: OLLAMA_MODEL
        value: mistral
      - key: HOST
        value: 0.0.0.0
      - key: PORT
        value: 10000
      - key: DEBUG
        value: false
      - key: CORS_ORIGINS
        sync: false  # À configurer avec l'URL Vercel
```

### Étape 2 : Créer `backend/requirements.txt` (si pas déjà fait)

Vérifiez que tous les packages sont listés :

```txt
# Core Framework
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic>=2.7.4
pydantic-settings==2.6.0

# Database Drivers
pymongo==4.6.1
neo4j==5.16.0
mysql-connector-python==8.3.0
sqlalchemy==2.0.25
greenlet==3.0.3

# SQL Parsing
sqlparse==0.4.4
sqlglot==20.11.0

# AI / ML APIs
langgraph==0.2.45
langchain-core==0.3.21
openai>=1.0.0

# Utilities
python-dotenv==1.0.0
python-multipart==0.0.6
aiofiles==23.2.1
httpx==0.26.0
pyyaml==6.0.1
email-validator==2.1.0.post1
orjson==3.9.15
tenacity==8.2.3
```

### Étape 3 : Déployer sur Render

#### Option A : Via Dashboard Render

1. **Connectez-vous à Render** : https://dashboard.render.com/

2. **Créer un nouveau Web Service** :
   - Cliquez sur "New +" → "Web Service"
   - Connectez votre repository GitHub
   - Sélectionnez le repository `sql-nosql-converter`

3. **Configuration** :
   ```
   Name: sql-nosql-backend
   Region: Frankfurt (ou le plus proche)
   Branch: main
   Root Directory: (laisser vide)
   Runtime: Python 3
   Build Command: pip install -r backend/requirements.txt
   Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
   Plan: Free
   ```

4. **Variables d'Environnement** :
   Ajoutez dans "Environment" :
   ```
   PYTHON_VERSION=3.13.0
   AI_PROVIDER=blazeapi
   BLAZEAPI_API_KEY=blz_votre_cle_ici
   BLAZEAPI_BASE_URL=https://blazeai.boxu.dev/api/
   BLAZEAPI_MODEL=claude-opus-4-7
   HOST=0.0.0.0
   PORT=10000
   DEBUG=false
   CORS_ORIGINS=https://votre-app.vercel.app
   ```

5. **Déployer** :
   - Cliquez sur "Create Web Service"
   - Attendez 5-10 minutes pour le build

6. **Récupérer l'URL** :
   - Une fois déployé, notez l'URL : `https://sql-nosql-backend.onrender.com`

#### Option B : Via render.yaml

1. Poussez `render.yaml` sur GitHub
2. Sur Render Dashboard, cliquez "New +" → "Blueprint"
3. Sélectionnez votre repository
4. Render détectera automatiquement `render.yaml`
5. Configurez les variables d'environnement manquantes
6. Cliquez "Apply"

### Étape 4 : Vérifier le Backend

```bash
# Test de santé
curl https://sql-nosql-backend.onrender.com/

# Devrait retourner :
# {
#   "status": "healthy",
#   "ai_provider": "blazeapi",
#   "ai_available": true
# }
```

---

## Déploiement Frontend (Vercel)

### Étape 1 : Créer `vercel.json`

Créez `vercel.json` à la racine du projet :

```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "frontend/dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ],
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### Étape 2 : Configurer l'URL du Backend

Créez `frontend/.env.production` :

```bash
VITE_API_URL=https://sql-nosql-backend.onrender.com
```

### Étape 3 : Mettre à jour `frontend/src/services/api.ts`

Vérifiez que l'API utilise la variable d'environnement :

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

### Étape 4 : Déployer sur Vercel

#### Option A : Via Vercel CLI

```bash
# Installer Vercel CLI
npm install -g vercel

# Se connecter
vercel login

# Déployer
cd frontend
vercel

# Suivre les instructions :
# ? Set up and deploy "~/sql-nosql-converter/frontend"? [Y/n] y
# ? Which scope? Your Account
# ? Link to existing project? [y/N] n
# ? What's your project's name? sql-nosql-converter
# ? In which directory is your code located? ./
# ? Want to override the settings? [y/N] n

# Déployer en production
vercel --prod
```

#### Option B : Via Dashboard Vercel

1. **Connectez-vous à Vercel** : https://vercel.com/dashboard

2. **Importer le Projet** :
   - Cliquez sur "Add New..." → "Project"
   - Sélectionnez votre repository GitHub
   - Cliquez "Import"

3. **Configuration** :
   ```
   Framework Preset: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

4. **Variables d'Environnement** :
   Ajoutez dans "Environment Variables" :
   ```
   VITE_API_URL=https://sql-nosql-backend.onrender.com
   ```

5. **Déployer** :
   - Cliquez sur "Deploy"
   - Attendez 2-5 minutes

6. **Récupérer l'URL** :
   - Une fois déployé, notez l'URL : `https://sql-nosql-converter.vercel.app`

### Étape 5 : Mettre à Jour CORS sur Render

Retournez sur Render et mettez à jour la variable `CORS_ORIGINS` :

```
CORS_ORIGINS=https://sql-nosql-converter.vercel.app,https://sql-nosql-converter-*.vercel.app
```

---

## Configuration Post-Déploiement

### 1. Configurer le Domaine Personnalisé (Optionnel)

#### Sur Vercel :
1. Allez dans "Settings" → "Domains"
2. Ajoutez votre domaine : `www.votre-domaine.com`
3. Configurez les DNS selon les instructions

#### Sur Render :
1. Allez dans "Settings" → "Custom Domain"
2. Ajoutez votre domaine : `api.votre-domaine.com`
3. Configurez les DNS selon les instructions

### 2. Activer HTTPS (Automatique)

- ✅ Vercel active HTTPS automatiquement
- ✅ Render active HTTPS automatiquement

### 3. Configurer les Logs

#### Render :
- Allez dans "Logs" pour voir les logs en temps réel
- Configurez les alertes dans "Settings" → "Notifications"

#### Vercel :
- Allez dans "Deployments" → Sélectionnez un déploiement → "Logs"
- Configurez les intégrations dans "Settings" → "Integrations"

---

## Vérification

### 1. Test Backend

```bash
# Health check
curl https://sql-nosql-backend.onrender.com/

# Test conversion
curl -X POST https://sql-nosql-backend.onrender.com/api/convert \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100));",
    "target_databases": ["mongodb"],
    "include_ai_explanation": true
  }'
```

### 2. Test Frontend

1. Ouvrez https://sql-nosql-converter.vercel.app/
2. Vérifiez que l'interface se charge
3. Testez une conversion SQL
4. Vérifiez que les résultats s'affichent

### 3. Test Intégration

1. Collez un SQL dans l'éditeur
2. Cliquez "Convert"
3. Vérifiez :
   - ✅ Barres de progression animées
   - ✅ Résultats pour 3 bases de données
   - ✅ JSON MongoDB réaliste
   - ✅ Explications AI détaillées
   - ✅ Temps de conversion < 10s

---

## Dépannage

### Problème 1 : Backend ne démarre pas sur Render

**Erreur :** `ModuleNotFoundError: No module named 'sqlglot'`

**Solution :**
```bash
# Vérifiez requirements.txt
cat backend/requirements.txt | grep sqlglot

# Si manquant, ajoutez :
echo "sqlglot==20.11.0" >> backend/requirements.txt

# Commit et push
git add backend/requirements.txt
git commit -m "Add sqlglot to requirements"
git push
```

### Problème 2 : CORS Error sur Frontend

**Erreur :** `Access to fetch at 'https://...' has been blocked by CORS policy`

**Solution :**
1. Sur Render, vérifiez `CORS_ORIGINS` :
   ```
   CORS_ORIGINS=https://sql-nosql-converter.vercel.app,https://sql-nosql-converter-*.vercel.app
   ```
2. Redémarrez le service Render
3. Attendez 1-2 minutes

### Problème 3 : Frontend ne se connecte pas au Backend

**Erreur :** `Failed to fetch` ou `Network Error`

**Solution :**
1. Vérifiez `VITE_API_URL` sur Vercel :
   ```
   VITE_API_URL=https://sql-nosql-backend.onrender.com
   ```
2. Redéployez le frontend :
   ```bash
   vercel --prod
   ```

### Problème 4 : BlazeAPI ne fonctionne pas

**Erreur :** `HTTP Error 403: Forbidden`

**Solution :**
1. Vérifiez `BLAZEAPI_API_KEY` sur Render
2. Testez la clé localement :
   ```bash
   curl -X POST https://blazeai.boxu.dev/api/chat/completions \
     -H "Authorization: Bearer blz_votre_cle" \
     -H "Content-Type: application/json" \
     -d '{"model":"claude-opus-4-7","messages":[{"role":"user","content":"test"}]}'
   ```

### Problème 5 : Render Free Tier s'endort

**Symptôme :** Première requête prend 30-60s

**Solution :**
1. **Accepter le délai** : C'est normal pour le plan gratuit
2. **Upgrade vers plan payant** : $7/mois pour instance toujours active
3. **Utiliser un service de ping** : https://uptimerobot.com (gratuit)
   - Ping toutes les 5 minutes pour garder l'instance active

### Problème 6 : Build échoue sur Vercel

**Erreur :** `npm ERR! code ELIFECYCLE`

**Solution :**
```bash
# Nettoyer et rebuilder localement
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build

# Si ça marche, commit et push
git add package-lock.json
git commit -m "Update package-lock.json"
git push
```

---

## 📊 Coûts Estimés

### Plan Gratuit (Recommandé pour Démarrer)

| Service | Plan | Coût | Limitations |
|---------|------|------|-------------|
| Render | Free | $0/mois | Instance s'endort après 15min d'inactivité |
| Vercel | Hobby | $0/mois | 100GB bandwidth/mois |
| BlazeAPI | Free Tier | $0/mois | Limites de requêtes |
| **Total** | | **$0/mois** | Parfait pour démo/test |

### Plan Production (Recommandé pour Usage Réel)

| Service | Plan | Coût | Avantages |
|---------|------|------|-----------|
| Render | Starter | $7/mois | Instance toujours active |
| Vercel | Pro | $20/mois | Bandwidth illimité, analytics |
| BlazeAPI | Paid | Variable | Plus de requêtes |
| **Total** | | **~$27/mois** | Production-ready |

---

## 🔒 Sécurité

### Variables d'Environnement Sensibles

**Ne JAMAIS commiter :**
- ❌ `BLAZEAPI_API_KEY`
- ❌ `MYSQL_PASSWORD`
- ❌ Toute clé API

**Toujours utiliser :**
- ✅ Variables d'environnement sur Render/Vercel
- ✅ `.env` en local (dans `.gitignore`)
- ✅ Secrets management

### HTTPS

- ✅ Activé automatiquement sur Vercel et Render
- ✅ Certificats SSL gratuits
- ✅ Renouvellement automatique

### Rate Limiting

Ajoutez dans `backend/main.py` :

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/convert")
@limiter.limit("10/minute")  # Max 10 conversions par minute
async def convert_schema(request: Request, conversion: ConversionRequest):
    ...
```

---

## 📚 Ressources Utiles

### Documentation
- [Render Docs](https://render.com/docs)
- [Vercel Docs](https://vercel.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Deployment](https://vitejs.dev/guide/static-deploy.html)

### Support
- Render Support: https://render.com/support
- Vercel Support: https://vercel.com/support
- GitHub Issues: https://github.com/votre-username/sql-nosql-converter/issues

---

## ✅ Checklist de Déploiement

### Avant le Déploiement
- [ ] Code poussé sur GitHub
- [ ] `requirements.txt` à jour
- [ ] `package.json` à jour
- [ ] Variables d'environnement documentées
- [ ] Tests locaux passent

### Backend (Render)
- [ ] Service créé sur Render
- [ ] Variables d'environnement configurées
- [ ] Build réussi
- [ ] Health check fonctionne
- [ ] CORS configuré

### Frontend (Vercel)
- [ ] Projet importé sur Vercel
- [ ] `VITE_API_URL` configurée
- [ ] Build réussi
- [ ] Interface accessible
- [ ] Connexion au backend fonctionne

### Post-Déploiement
- [ ] Test de conversion complet
- [ ] Vérification des logs
- [ ] Configuration des alertes
- [ ] Documentation mise à jour
- [ ] Domaine personnalisé (optionnel)

---

## 🎉 Félicitations !

Votre application est maintenant déployée et accessible publiquement !

**URLs :**
- Frontend : https://sql-nosql-converter.vercel.app
- Backend : https://sql-nosql-backend.onrender.com
- API Docs : https://sql-nosql-backend.onrender.com/docs

**Prochaines Étapes :**
1. Partagez l'URL avec vos utilisateurs
2. Configurez les analytics (Vercel Analytics)
3. Ajoutez un domaine personnalisé
4. Configurez les alertes de monitoring
5. Planifiez les mises à jour

---

**Version:** 3.0.2  
**Dernière Mise à Jour:** 28 avril 2026  
**Auteur:** Kiro AI Assistant

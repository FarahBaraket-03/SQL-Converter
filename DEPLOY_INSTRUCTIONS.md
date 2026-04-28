# 🚀 Instructions de Déploiement Simplifiées

## Problème Résolu: Dépendances

Le fichier `requirements.txt` a été mis à jour pour éviter les conflits de dépendances:
- ✅ Suppression de `orjson` (nécessite compilation)
- ✅ Suppression de `greenlet` (dépendance automatique)
- ✅ Versions flexibles pour éviter les conflits
- ✅ Python 3.11.9 spécifié dans `runtime.txt`

---

## 🎯 Déploiement Backend sur Render

### Méthode 1: Render Dashboard (Recommandé)

1. **Créer un compte sur [Render](https://render.com)**

2. **Nouveau Web Service:**
   - Cliquez sur "New +" → "Web Service"
   - Connectez votre GitHub
   - Sélectionnez `SQL-Converter`

3. **Configuration:**
   ```
   Name: sql-nosql-converter-api
   Region: Oregon (US West)
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install --upgrade pip && pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   Plan: Free
   ```

4. **Variables d'Environnement:**
   ```
   AI_PROVIDER=blazeapi
   BLAZEAPI_API_KEY=blz_your_key_here
   BLAZEAPI_BASE_URL=https://blazeai.boxu.dev/api/
   BLAZEAPI_MODEL=claude-opus-4-7
   CORS_ORIGINS=https://your-app.vercel.app
   DEBUG=false
   ```

5. **Déployer** → Attendez 5-10 minutes

### Méthode 2: Render avec render.yaml (Automatique)

Le fichier `render.yaml` est déjà configuré:

1. Connectez votre repo à Render
2. Render détecte automatiquement `render.yaml`
3. Ajoutez `BLAZEAPI_API_KEY` manuellement
4. Déployez!

---

## 🎨 Déploiement Frontend sur Vercel

### Méthode 1: Vercel Dashboard

1. **Créer un compte sur [Vercel](https://vercel.com)**

2. **Nouveau Projet:**
   - Cliquez sur "Add New..." → "Project"
   - Importez `SQL-Converter`
   - Root Directory: `frontend`

3. **Configuration:**
   ```
   Framework Preset: Vite
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

4. **Variables d'Environnement:**
   ```
   VITE_API_URL=https://sql-nosql-converter-api.onrender.com
   ```

5. **Déployer** → Prêt en 2 minutes!

### Méthode 2: Vercel CLI

```bash
cd frontend
npm install -g vercel
vercel login
vercel --prod
```

---

## 🔧 Dépannage

### Erreur: "orjson compilation failed"

✅ **Résolu**: `orjson` supprimé du `requirements.txt`

### Erreur: "Python version mismatch"

✅ **Résolu**: `runtime.txt` spécifie Python 3.11.9

### Erreur: "Module not found"

```bash
# Vérifier les dépendances
pip install -r backend/requirements.txt

# Tester localement
cd backend
uvicorn main:app --reload
```

### Erreur: "CORS policy"

Vérifiez que `CORS_ORIGINS` contient l'URL de votre frontend Vercel.

---

## ✅ Vérification Post-Déploiement

### Backend (Render)

1. Ouvrez: `https://your-api.onrender.com`
2. Devrait afficher: `{"status":"healthy","ai_provider":"blazeapi","ai_available":true}`

### Frontend (Vercel)

1. Ouvrez: `https://your-app.vercel.app`
2. Testez une conversion SQL
3. Vérifiez que l'API répond

---

## 📊 Fichiers de Configuration

| Fichier | Description |
|---------|-------------|
| `backend/requirements.txt` | Dépendances Python (sans orjson) |
| `backend/runtime.txt` | Version Python (3.11.9) |
| `backend/Procfile` | Commande de démarrage Render |
| `render.yaml` | Configuration automatique Render |
| `frontend/vercel.json` | Configuration Vercel |

---

## 🎉 Résultat Final

- **Backend**: `https://sql-nosql-converter-api.onrender.com`
- **Frontend**: `https://sql-nosql-converter.vercel.app`
- **Temps total**: ~15 minutes
- **Coût**: Gratuit (plans Free)

---

## 📚 Ressources

- [Render Documentation](https://render.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Deployment](https://vitejs.dev/guide/static-deploy.html)

---

**Date:** 28 avril 2026  
**Version:** 3.0.0  
**Status:** ✅ Prêt pour le déploiement

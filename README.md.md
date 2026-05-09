# EduAI — Récapitulatif du projet

> **Projet de Fin d'Études · 2025–2026**
> Nizar Benmsika · Master Cybersécurité & Intelligence Artificielle
> Plateforme de gestion scolaire intelligente

---

## 📊 État d'avancement

| Phase | Mois | Statut | Détail |
|-------|------|--------|--------|
| 1 | Mois 1 | ✅ **100%** | Application web complète |
| 2 | Mois 2 | ✅ **100%** | Docker (3 conteneurs) |
| 3 | Mois 3 | ❌ 0% | Chatbot Ollama |
| 4 | Mois 4 | ❌ 0% | Sécurité, tests, mémoire |

**Position actuelle : 50% du projet, en avance sur le planning.**

---

## 🎯 Le sujet

Le PFE repose sur **3 piliers non-négociables** demandés par le prof :

1. **Application web complète** (frontend + backend + base SQL)
2. **Containerisation Docker**
3. **Chatbot intelligent basé sur un LLM** (Ollama)

Le contexte métier choisi : gestion d'une **école primaire marocaine**.

---

## 🏗️ Architecture

```
┌───────────────────────────────────────────────────────────┐
│                  DOCKER · docker-compose                   │
│                                                            │
│   ┌──────────┐    ┌──────────┐    ┌──────────────┐        │
│   │ Frontend │───▶│ Backend  │───▶│ PostgreSQL   │        │
│   │ nginx    │    │ FastAPI  │    │ 4 tables     │        │
│   │ :8080    │    │ :8000    │    │ :5432        │        │
│   └──────────┘    └──────────┘    └──────────────┘        │
│                        │                                   │
│                        ▼                                   │
│                  ┌──────────┐                              │
│                  │ Ollama   │  ← À venir (Mois 3)         │
│                  │ LLM      │                              │
│                  └──────────┘                              │
└───────────────────────────────────────────────────────────┘
```

---

## 📁 Structure des fichiers

```
pfe_ai_project/
│
├── backend/
│   ├── main.py              ← API FastAPI (20 endpoints)
│   ├── requirements.txt     ← Dépendances Python
│   ├── .env                 ← DATABASE_URL local
│   └── Dockerfile           ← Image backend
│
├── frontend/
│   ├── index.html           ← App EduAI (HTML+CSS+JS)
│   ├── Dockerfile           ← Image nginx
│   └── nginx.conf           ← Config serveur web
│
├── database/
│   └── init.sql             ← Schéma + données réelles
│
├── docker-compose.yml       ← Orchestration des 3 services
└── .env                     ← Variables Docker (DB_USER, etc.)
```

---

## 💾 Base de données

**4 tables liées** :

| Table | Rôle | Volume actuel |
|-------|------|---------------|
| `classes` | Niveaux scolaires (1APG-1, 2APG-1...) | 12 |
| `matieres` | Disciplines enseignées | 8 |
| `etudiants` | Élèves inscrits | 236 |
| `notes` | Évaluations sur 20 | 1879 |

**Moyenne générale actuelle : 12.44/20**

### Relations clés

- `etudiants.classe_id` → `classes.id` (un élève appartient à une classe)
- `notes.etudiant_id` → `etudiants.id` (une note appartient à un élève)
- `notes.matiere_id` → `matieres.id` (une note concerne une matière)

### Contraintes métier

- `note FLOAT CHECK (note >= 0 AND note <= 20)` — note entre 0 et 20
- `nom_classe UNIQUE` — pas de classes en doublon
- `nom_matiere UNIQUE` — pas de matières en doublon
- `code_etudiant UNIQUE` — pas de codes en doublon

---

## 🔌 Backend FastAPI — 20 endpoints

### Étudiants

- `GET    /etudiants` — liste tous
- `GET    /etudiants_details` — avec nom de classe (JOIN)
- `GET    /etudiants/{id}` — un seul
- `POST   /etudiants` — créer
- `PUT    /etudiants/{id}` — modifier
- `DELETE /etudiants/{id}` — supprimer (cascade sur notes)

### Classes

- `GET    /classes`
- `GET    /classes/{id}`
- `POST   /classes`
- `PUT    /classes/{id}`
- `DELETE /classes/{id}` — refuse si élèves dedans

### Matières

- `GET    /matieres`
- `GET    /matieres/{id}`
- `POST   /matieres`
- `PUT    /matieres/{id}`
- `DELETE /matieres/{id}` — refuse si notes dessus

### Notes

- `GET    /notes`
- `GET    /notes_details` — avec nom élève + matière (triple JOIN)
- `GET    /notes/{id}`
- `POST   /notes`
- `PUT    /notes/{id}`
- `DELETE /notes/{id}`

### Documentation auto

Toutes les routes sont testables via Swagger : http://localhost:8000/docs

---

## 🎨 Frontend EduAI

**Stack :** HTML/CSS/JavaScript vanilla, sans framework
**Design :** dark moderne, gradients violet/rose, typographie Bricolage Grotesque
**Sections :** Tableau de bord · Élèves · Classes · Matières · Notes
**Bonus :** panneau de chat EduBot intégré (mode démo, prêt pour Ollama)

### Fonctionnalités

- ✅ Création d'élèves, classes, matières, notes (POST)
- ✅ Liste avec recherche par section (GET)
- ✅ Modification via modale popup (PUT)
- ✅ Suppression avec confirmation (DELETE)
- ✅ Toast de feedback sur chaque action
- ✅ Chat EduBot avec réponses sur vraies données
- ✅ Responsive (s'adapte mobile/tablette)

---

## 🐳 Commandes Docker essentielles

### Démarrer le projet

```bash
cd C:\Users\Nizar\Desktop\pfe_ai_project
docker-compose up
```

Puis ouvrir :
- **App** : http://localhost:8080
- **API Swagger** : http://localhost:8000/docs

### Arrêter proprement (en gardant les données)

```bash
docker-compose down
```

### Reconstruire après modification du code

```bash
docker-compose up --build
```

### Tout effacer (y compris la base de données) ⚠

```bash
docker-compose down -v
```

À utiliser **uniquement** pour repartir de zéro avec un `init.sql` modifié.

### Voir les logs en direct

```bash
docker-compose logs -f
```

### Voir l'état des conteneurs

```bash
docker-compose ps
```

---

## 🛠️ Commandes utiles (mode local sans Docker)

Ces commandes servent si tu veux relancer le backend hors Docker (par exemple pour debug rapide) :

```bash
cd C:\Users\Nizar\Desktop\pfe_ai_project\backend
uvicorn main:app --reload
```

Avec Docker, ce n'est plus nécessaire — Docker fait tout.

---

## ⚠️ Pièges fréquents et solutions

### "Could not import module main"

**Cause :** uvicorn lancé du mauvais dossier
**Solution :** `cd backend` avant de lancer

### CORS bloque les appels API

**Cause :** middleware CORS pas activé
**Solution :** déjà présent dans `main.py` :

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Docker affiche 0 élèves après docker-compose up

**Cause :** ancienne base persistée dans le volume
**Solution :** `docker-compose down -v` puis `docker-compose up --build`

### Mot de passe DB en dur dans le code

**Cause :** mauvaise pratique de sécurité
**Solution :** utiliser `.env` + `python-dotenv`, déjà fait

---

## 🔐 Configuration des variables d'environnement

### `.env` à la racine (pour Docker)

```
DB_USER=postgres
DB_PASSWORD=1232
DB_NAME=pfe_db
```

### `backend/.env` (pour mode local)

```
DATABASE_URL=postgresql://postgres:1232@localhost:5432/pfe_db
```

---

## 📦 Dépendances Python (`requirements.txt`)

```
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlalchemy==2.0.36
psycopg2-binary==2.9.10
pydantic==2.9.2
python-dotenv==1.0.1
```

---

## 🤖 Ce qui reste à faire — Mois 3 : Ollama

### À installer dans Docker

Ajouter un 4ème service au `docker-compose.yml` :

```yaml
ollama:
  image: ollama/ollama
  container_name: eduai_ollama
  ports:
    - "11434:11434"
  volumes:
    - ollama_data:/root/.ollama
```

Et télécharger un modèle :

```bash
docker exec -it eduai_ollama ollama pull llama3:8b
```

### À ajouter au backend

Un nouvel endpoint `POST /chat` qui :

1. **Reçoit** une question en langage naturel
2. **Reconnaît** via mots-clés ("combien", "moyenne", "élèves", etc.)
3. **Exécute** une requête SQL prédéfinie sur la base
4. **Envoie** le résultat à Ollama avec un prompt
5. **Renvoie** la reformulation naturelle

### À adapter dans le frontend

Dans `index.html`, remplacer la fonction `localKeywordBot()` par :

```javascript
async function askAI(q) {
  const r = await fetch(API + '/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ question: q })
  });
  return (await r.json()).response;
}
```

(4 lignes à changer, le reste du chat fonctionne déjà.)

### Choix stratégique (déjà fait)

**Approche choisie : keyword matching + LLM reformulation** (pas Text-to-SQL).

> Le LLM ne génère **jamais** de SQL — il reformule juste les résultats.
> Plus stable, plus sûr, plus défendable en soutenance.

---

## 🎯 Mois 4 — Ce qui reste

- **Sécurité** : audit, validation entrées, anti-injection (déjà partiellement fait avec paramètres nommés)
- **Tests** : intégration sur les endpoints critiques
- **Mémoire** : rédaction du document final (~30-50 pages)
- **Soutenance** : préparation présentation + démo + Q/R

---

## 💬 Phrase-clé pour la soutenance

> *"Mon projet entier — base de données, backend, frontend — se lance avec une seule commande : `docker-compose up`. Pas besoin d'installer Python, ni PostgreSQL, ni quoi que ce soit. La base est peuplée automatiquement avec 236 étudiants et 1879 notes réelles."*

C'est ce qui distingue un PFE moyen d'un PFE pro.

---

## 🔗 URLs importantes

| Service | URL | Quand |
|---------|-----|-------|
| Application EduAI | http://localhost:8080 | Démo principale |
| API Swagger | http://localhost:8000/docs | Tester les endpoints |
| API Backend | http://localhost:8000 | Pour le frontend |
| PostgreSQL | localhost:5432 | Pour pgAdmin |

---

## 📝 Notes personnelles à compléter

> Cette section est pour toi : ajoute ici les remarques de ton encadrant, les changements demandés, les idées qui te viennent…

```
[à remplir au fil du projet]
```

---

*Document généré le 8 mai 2026. Mis à jour à la fin de la phase 2 (Docker).*

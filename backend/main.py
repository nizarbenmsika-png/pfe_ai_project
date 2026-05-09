"""
EduAI — API Backend
Gestion académique : étudiants, classes, matières, notes.

Endpoints :
  Étudiants  : GET, POST, PUT, DELETE /etudiants[/{id}]
  Classes    : GET, POST, PUT, DELETE /classes[/{id}]
  Matières   : GET, POST, PUT, DELETE /matieres[/{id}]
  Notes      : GET, POST, PUT, DELETE /notes[/{id}]
  Détails    : /etudiants_details, /notes_details (avec JOIN)
"""

import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

# ════════════════════════════════════════════════════════════════
# CONFIGURATION
# ════════════════════════════════════════════════════════════════

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:1232@localhost:5432/pfe_db"
)

engine = create_engine(DATABASE_URL)

app = FastAPI(
    title="EduAI API",
    version="2.0",
    description="Backend de gestion académique pour école primaire."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ════════════════════════════════════════════════════════════════
# MODÈLES
# ════════════════════════════════════════════════════════════════

class EtudiantIn(BaseModel):
    code_etudiant: str = Field(..., min_length=1, max_length=20)
    nom: str = Field(..., min_length=1, max_length=100)
    prenom: str = Field(..., min_length=1, max_length=100)
    date_naissance: str
    classe_id: Optional[int] = None


class EtudiantUpdate(BaseModel):
    code_etudiant: Optional[str] = Field(None, min_length=1, max_length=20)
    nom: Optional[str] = Field(None, min_length=1, max_length=100)
    prenom: Optional[str] = Field(None, min_length=1, max_length=100)
    date_naissance: Optional[str] = None
    classe_id: Optional[int] = None


class ClasseIn(BaseModel):
    nom_classe: str = Field(..., min_length=1, max_length=50)


class MatiereIn(BaseModel):
    nom_matiere: str = Field(..., min_length=1, max_length=100)


class NoteIn(BaseModel):
    etudiant_id: int
    matiere_id: int
    note: float = Field(..., ge=0, le=20)


class NoteUpdate(BaseModel):
    note: float = Field(..., ge=0, le=20)


# ════════════════════════════════════════════════════════════════
# HELPER
# ════════════════════════════════════════════════════════════════

def ensure_exists(conn, table: str, entity_label: str, id: int):
    """Vérifie qu'un enregistrement existe, sinon lève une 404."""
    row = conn.execute(
        text(f"SELECT id FROM {table} WHERE id = :id"),
        {"id": id}
    ).fetchone()
    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"{entity_label} #{id} introuvable"
        )


# ════════════════════════════════════════════════════════════════
# ROOT
# ════════════════════════════════════════════════════════════════

@app.get("/")
def read_root():
    return {
        "api": "EduAI",
        "version": "2.0",
        "status": "ok",
        "docs": "/docs"
    }


# ════════════════════════════════════════════════════════════════
# ÉTUDIANTS
# ════════════════════════════════════════════════════════════════

@app.get("/etudiants")
def list_etudiants():
    """Liste tous les étudiants."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM etudiants ORDER BY id"))
        return [dict(r._mapping) for r in result]


@app.get("/etudiants_details")
def list_etudiants_details():
    """Liste des étudiants avec leur classe (jointure)."""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT e.id, e.code_etudiant, e.nom, e.prenom,
                   e.date_naissance, e.classe_id, c.nom_classe
            FROM etudiants e
            LEFT JOIN classes c ON e.classe_id = c.id
            ORDER BY e.id
        """))
        return [dict(r._mapping) for r in result]


@app.get("/etudiants/{id}")
def get_etudiant(id: int):
    """Récupère un étudiant par son ID."""
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT * FROM etudiants WHERE id = :id"),
            {"id": id}
        ).fetchone()
        if not row:
            raise HTTPException(404, f"Étudiant #{id} introuvable")
        return dict(row._mapping)


@app.post("/etudiants", status_code=201)
def create_etudiant(etudiant: EtudiantIn):
    """Inscrit un nouvel étudiant."""
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO etudiants
                    (code_etudiant, nom, prenom, date_naissance, classe_id)
                VALUES (:code, :nom, :prenom, :date, :classe)
            """), {
                "code": etudiant.code_etudiant,
                "nom": etudiant.nom,
                "prenom": etudiant.prenom,
                "date": etudiant.date_naissance,
                "classe": etudiant.classe_id
            })
            conn.commit()
        return {"message": "Étudiant inscrit avec succès"}
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Code étudiant déjà existant ou classe invalide"
        )


@app.put("/etudiants/{id}")
def update_etudiant(id: int, etudiant: EtudiantUpdate):
    """Modifie un étudiant (partiel : seuls les champs fournis sont mis à jour)."""
    updates = {k: v for k, v in etudiant.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(422, "Aucune donnée à modifier")

    with engine.connect() as conn:
        ensure_exists(conn, "etudiants", "Étudiant", id)

        set_clause = ", ".join(f"{k} = :{k}" for k in updates)
        try:
            conn.execute(
                text(f"UPDATE etudiants SET {set_clause} WHERE id = :id"),
                {**updates, "id": id}
            )
            conn.commit()
            return {"message": "Étudiant modifié"}
        except IntegrityError:
            raise HTTPException(409, "Conflit de données (code en doublon ou classe invalide)")


@app.delete("/etudiants/{id}")
def delete_etudiant(id: int):
    """Supprime un étudiant. Ses notes sont supprimées automatiquement."""
    with engine.connect() as conn:
        ensure_exists(conn, "etudiants", "Étudiant", id)
        conn.execute(text("DELETE FROM notes WHERE etudiant_id = :id"), {"id": id})
        conn.execute(text("DELETE FROM etudiants WHERE id = :id"), {"id": id})
        conn.commit()
        return {"message": "Étudiant supprimé (et ses notes)"}


# ════════════════════════════════════════════════════════════════
# CLASSES
# ════════════════════════════════════════════════════════════════

@app.get("/classes")
def list_classes():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM classes ORDER BY id"))
        return [dict(r._mapping) for r in result]


@app.get("/classes/{id}")
def get_classe(id: int):
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT * FROM classes WHERE id = :id"),
            {"id": id}
        ).fetchone()
        if not row:
            raise HTTPException(404, f"Classe #{id} introuvable")
        return dict(row._mapping)


@app.post("/classes", status_code=201)
def create_classe(classe: ClasseIn):
    try:
        with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO classes (nom_classe) VALUES (:nom)"),
                {"nom": classe.nom_classe}
            )
            conn.commit()
        return {"message": "Classe ajoutée"}
    except IntegrityError:
        raise HTTPException(409, "Cette classe existe déjà")


@app.put("/classes/{id}")
def update_classe(id: int, classe: ClasseIn):
    with engine.connect() as conn:
        ensure_exists(conn, "classes", "Classe", id)
        try:
            conn.execute(
                text("UPDATE classes SET nom_classe = :nom WHERE id = :id"),
                {"nom": classe.nom_classe, "id": id}
            )
            conn.commit()
            return {"message": "Classe modifiée"}
        except IntegrityError:
            raise HTTPException(409, "Ce nom de classe existe déjà")


@app.delete("/classes/{id}")
def delete_classe(id: int):
    """Supprime une classe. Refuse si elle contient des étudiants."""
    with engine.connect() as conn:
        ensure_exists(conn, "classes", "Classe", id)

        count = conn.execute(
            text("SELECT COUNT(*) FROM etudiants WHERE classe_id = :id"),
            {"id": id}
        ).scalar()
        if count and count > 0:
            raise HTTPException(
                409,
                f"Impossible de supprimer : {count} étudiant(s) dans cette classe."
            )

        conn.execute(text("DELETE FROM classes WHERE id = :id"), {"id": id})
        conn.commit()
        return {"message": "Classe supprimée"}


# ════════════════════════════════════════════════════════════════
# MATIÈRES
# ════════════════════════════════════════════════════════════════

@app.get("/matieres")
def list_matieres():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM matieres ORDER BY id"))
        return [dict(r._mapping) for r in result]


@app.get("/matieres/{id}")
def get_matiere(id: int):
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT * FROM matieres WHERE id = :id"),
            {"id": id}
        ).fetchone()
        if not row:
            raise HTTPException(404, f"Matière #{id} introuvable")
        return dict(row._mapping)


@app.post("/matieres", status_code=201)
def create_matiere(matiere: MatiereIn):
    try:
        with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO matieres (nom_matiere) VALUES (:nom)"),
                {"nom": matiere.nom_matiere}
            )
            conn.commit()
        return {"message": "Matière ajoutée"}
    except IntegrityError:
        raise HTTPException(409, "Cette matière existe déjà")


@app.put("/matieres/{id}")
def update_matiere(id: int, matiere: MatiereIn):
    with engine.connect() as conn:
        ensure_exists(conn, "matieres", "Matière", id)
        try:
            conn.execute(
                text("UPDATE matieres SET nom_matiere = :nom WHERE id = :id"),
                {"nom": matiere.nom_matiere, "id": id}
            )
            conn.commit()
            return {"message": "Matière modifiée"}
        except IntegrityError:
            raise HTTPException(409, "Ce nom de matière existe déjà")


@app.delete("/matieres/{id}")
def delete_matiere(id: int):
    """Supprime une matière. Refuse s'il existe des notes dessus."""
    with engine.connect() as conn:
        ensure_exists(conn, "matieres", "Matière", id)

        count = conn.execute(
            text("SELECT COUNT(*) FROM notes WHERE matiere_id = :id"),
            {"id": id}
        ).scalar()
        if count and count > 0:
            raise HTTPException(
                409,
                f"Impossible de supprimer : {count} note(s) sur cette matière."
            )

        conn.execute(text("DELETE FROM matieres WHERE id = :id"), {"id": id})
        conn.commit()
        return {"message": "Matière supprimée"}


# ════════════════════════════════════════════════════════════════
# NOTES
# ════════════════════════════════════════════════════════════════

@app.get("/notes")
def list_notes():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM notes ORDER BY id"))
        return [dict(r._mapping) for r in result]


@app.get("/notes_details")
def list_notes_details():
    """Liste des notes avec nom d'élève et de matière (jointure)."""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT n.id, n.note,
                   e.id AS etudiant_id, e.nom, e.prenom,
                   m.id AS matiere_id, m.nom_matiere
            FROM notes n
            JOIN etudiants e ON n.etudiant_id = e.id
            JOIN matieres m ON n.matiere_id = m.id
            ORDER BY n.id
        """))
        return [dict(r._mapping) for r in result]


@app.get("/notes/{id}")
def get_note(id: int):
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT * FROM notes WHERE id = :id"),
            {"id": id}
        ).fetchone()
        if not row:
            raise HTTPException(404, f"Note #{id} introuvable")
        return dict(row._mapping)


@app.post("/notes", status_code=201)
def create_note(note: NoteIn):
    """Enregistre une nouvelle note (entre 0 et 20)."""
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO notes (etudiant_id, matiere_id, note)
                VALUES (:etudiant, :matiere, :note)
            """), {
                "etudiant": note.etudiant_id,
                "matiere": note.matiere_id,
                "note": note.note
            })
            conn.commit()
        return {"message": "Note enregistrée"}
    except IntegrityError:
        raise HTTPException(409, "Étudiant ou matière inexistant")


@app.put("/notes/{id}")
def update_note(id: int, note: NoteUpdate):
    """Modifie la valeur d'une note."""
    with engine.connect() as conn:
        ensure_exists(conn, "notes", "Note", id)
        conn.execute(
            text("UPDATE notes SET note = :note WHERE id = :id"),
            {"note": note.note, "id": id}
        )
        conn.commit()
        return {"message": "Note modifiée"}


@app.delete("/notes/{id}")
def delete_note(id: int):
    with engine.connect() as conn:
        ensure_exists(conn, "notes", "Note", id)
        conn.execute(text("DELETE FROM notes WHERE id = :id"), {"id": id})
        conn.commit()
        return {"message": "Note supprimée"}
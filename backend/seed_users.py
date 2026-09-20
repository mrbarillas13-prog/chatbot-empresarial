"""Crea los usuarios iniciales (admin y cliente) leyendo las contraseñas de variables de entorno.

Uso:
    export SEED_ADMIN_PASSWORD='...'
    export SEED_CLIENT_PASSWORD='...'
    python seed_users.py

Las contraseñas NUNCA se escriben en el código: este repositorio es público.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine, Base  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services.auth_service import hash_password  # noqa: E402

admin_username = os.getenv("SEED_ADMIN_USER", "admin")
admin_password = os.getenv("SEED_ADMIN_PASSWORD")
client_username = os.getenv("SEED_CLIENT_USER", "client")
client_password = os.getenv("SEED_CLIENT_PASSWORD")

if not admin_password or not client_password:
    raise SystemExit(
        "Faltan SEED_ADMIN_PASSWORD y/o SEED_CLIENT_PASSWORD.\n"
        "Pásalas como variables de entorno; no se guardan en el repositorio."
    )

Base.metadata.create_all(bind=engine)
db = SessionLocal()


def create_if_missing(username: str, password: str, role: str) -> None:
    if db.query(User).filter(User.username == username).first():
        print(f"usuario ya existe, sin cambios: {username}")
        return
    db.add(User(username=username, password_hash=hash_password(password), role=role))
    db.commit()
    print(f"usuario creado: {username} ({role})")


create_if_missing(admin_username, admin_password, "admin")
create_if_missing(client_username, client_password, "client")
db.close()

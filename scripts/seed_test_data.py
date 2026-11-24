"""Datos de prueba para probar permisos: 2 roles y 2 usuarios (admin y usuario normal).

SOLO PARA UNA BASE DE DATOS DE DESARROLLO/PRUEBAS. Es idempotente: se puede ejecutar varias veces
(los roles se actualizan por nombre y los usuarios se omiten si el correo ya existe).

Uso (desde la raíz del proyecto):
    python scripts/seed_test_data.py --dry-run     # genera los hashes y muestra el plan, sin tocar la BD
    python scripts/seed_test_data.py               # inserta (pide confirmación)

Las contraseñas se leen de las variables de entorno SEED_ADMIN_PASSWORD y SEED_USER_PASSWORD;
si no existen, se piden por consola sin mostrarlas.
"""
import argparse
import asyncio
import getpass
import json
import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sqlalchemy import text  # noqa: E402
from sqlalchemy.engine import make_url  # noqa: E402

from core.permissions.bitmask_engine import ActionsPermissions, SystemModules  # noqa: E402
from core.security.password import hash_password  # noqa: E402
from db.config import DBConfig  # noqa: E402
from db.connection import engine  # noqa: E402

SEED_PCID = "seed-script"
SEED_CREATED_BY = uuid.uuid4()  # el campo creado_por es NOT NULL; no es FK

ALL_ACTIONS = int(
    ActionsPermissions.PERM_READ | ActionsPermissions.PERM_CREATE | ActionsPermissions.PERM_UPDATE
    | ActionsPermissions.PERM_DELETE | ActionsPermissions.PERM_EXPORT
)  # 31
READ_ONLY = int(ActionsPermissions.PERM_READ)  # 1

ROLES = [
    {
        "nombre": "Administrador (prueba)",
        "permissions": {SystemModules.AUTH.value: ALL_ACTIONS, SystemModules.USER.value: ALL_ACTIONS},
    },
    {
        "nombre": "Usuario estándar (prueba)",
        "permissions": {SystemModules.AUTH.value: READ_ONLY, SystemModules.USER.value: READ_ONLY},
    },
]

USERS = [
    {"email": "erialdev@icloud.com", "nombre": "Admin", "apellido": "Prueba",
     "rol": "Administrador (prueba)", "password_env": "SEED_ADMIN_PASSWORD"},
    {"email": "erick.alvears@ug.edu.ec", "nombre": "Usuario", "apellido": "Prueba",
     "rol": "Usuario estándar (prueba)", "password_env": "SEED_USER_PASSWORD"},
]

UPSERT_ROLE = text("""
    INSERT INTO sis_roles (nombre, version, permissions, creado_por, pcid)
    VALUES (:nombre, 1, CAST(:permissions AS json), :creado_por, :pcid)
    ON CONFLICT (nombre) DO UPDATE
        SET permissions = EXCLUDED.permissions,
            version = sis_roles.version + 1,
            editado_por = :creado_por,
            fecha_editado = NOW()
    RETURNING id
""")

INSERT_USER = text("""
    INSERT INTO sis_usuarios (contrasena, email_est, nombre, apellido, rol_id, creado_por, pcid)
    VALUES (:contrasena, :email, :nombre, :apellido, :rol_id, :creado_por, :pcid)
    ON CONFLICT (email_est) DO NOTHING
    RETURNING id
""")


def read_password(env_name: str, label: str) -> str:
    value = os.getenv(env_name) or getpass.getpass(f"Contraseña para {label}: ")
    if len(value) < 8:
        sys.exit(f"La contraseña de {label} debe tener al menos 8 caracteres.")
    return value


def describe_target() -> str:
    url = make_url(DBConfig.database_url)
    return f"{url.host}:{url.port or 5432}/{url.database}"  # sin usuario ni contraseña


async def main(dry_run: bool) -> None:
    engine.sync_engine.echo = False  # evita imprimir los hashes en el log de SQLAlchemy

    hashes = {u["email"]: hash_password(read_password(u["password_env"], u["email"])) for u in USERS}

    print(f"\nBase de datos destino: {describe_target()}")
    for role in ROLES:
        print(f"  rol     : {role['nombre']:<28} permisos={json.dumps(role['permissions'])}")
    for user in USERS:
        print(f"  usuario : {user['email']:<28} rol={user['rol']}")

    if dry_run:
        print("\n--dry-run: hashes generados correctamente; no se tocó la base de datos.")
        return

    if input("\nEscribe SI para insertar en esa base de datos: ").strip() != "SI":
        sys.exit("Cancelado.")

    async with engine.begin() as conn:
        role_ids: dict[str, int] = {}
        for role in ROLES:
            result = await conn.execute(UPSERT_ROLE, {
                "nombre": role["nombre"], "permissions": json.dumps(role["permissions"]),
                "creado_por": SEED_CREATED_BY, "pcid": SEED_PCID,
            })
            role_ids[role["nombre"]] = result.scalar_one()

        for user in USERS:
            result = await conn.execute(INSERT_USER, {
                "contrasena": hashes[user["email"]], "email": user["email"], "nombre": user["nombre"],
                "apellido": user["apellido"], "rol_id": role_ids[user["rol"]],
                "creado_por": SEED_CREATED_BY, "pcid": SEED_PCID,
            })
            created = result.scalar_one_or_none()
            print(f"  {user['email']}: " + (f"creado (id {created})" if created else "ya existía, se omitió"))

    await engine.dispose()
    print("\nListo. Roles:", role_ids)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="No toca la base de datos")
    # En Windows el loop por defecto (Proactor) no es compatible con psycopg en modo async
    asyncio.run(main(parser.parse_args().dry_run), loop_factory=asyncio.SelectorEventLoop)

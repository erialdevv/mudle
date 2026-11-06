from sqlalchemy import(
    Table,
    Column,
    String
)

from db.columnas_base import columnas_base, metadata


usuario_tabla=Table(
    'sis_usuarios',
     metadata,
     Column("contrasena",String(255),nullable=False),
     Column("email_est",String(254),nullable=False, index=True, unique=True),
     Column("nombre",String(150), nullable=True),
     Column("apellido",String(150), nullable=True),
     *columnas_base(),
)

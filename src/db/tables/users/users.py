from sqlalchemy import(
    Table,
    Column,
    String,
    BigInteger,
    ForeignKey
)

from db.base_columns import base_columns, metadata


users_table=Table(
    'sis_usuarios',
     metadata,
     Column("contrasena",String(255),nullable=False),
     Column("email_est",String(254),nullable=False, index=True, unique=True),
     Column("nombre",String(150), nullable=True),
     Column("apellido",String(150), nullable=True),
     Column("rol_id",BigInteger, ForeignKey("sis_roles.id", ondelete="RESTRICT"), nullable=False, index=True),
     *base_columns(),
)

from sqlalchemy import(
    Table,
    Column,
    String,
    Date,
    ForeignKey,
    Uuid
)

from db.columnas_base import columnas_base, metadata


usuario_tabla=Table(
    'sis_estudiantes',
     metadata,
     Column("codigo",String(10),unique=True, nullable=False),
     Column("usuario_id",Uuid(as_uuid=True),ForeignKey("usuarios.id", ondelete="RESTRICT"),nullable=False, unique=True),
     Column("fecha_nacimiento", Date, nullable=False),
     Column("email_personal",String(254),nullable=True),
     *columnas_base(),
)

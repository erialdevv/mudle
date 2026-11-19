from sqlalchemy import (
    Table,
    Column,
    String,
    Integer,
    JSON
)
from db.base_columns import metadata,base_columns

roles=Table(
    "sis_roles",
    metadata,
    Column("nombre",String(150), unique=True,nullable=False),
    Column("version",Integer, default=1, nullable=False),
    Column("permissions",JSON, nullable=False, server_default=dict)
    *base_columns()
)
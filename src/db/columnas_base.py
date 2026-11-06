from sqlalchemy import (
    Column,
    String,
    Uuid,
    DateTime,
    func,
    Boolean,
    MetaData,
    BigInteger,
    text
)


metadata = MetaData()


def columnas_base():
    columnas = [
        Column("id",BigInteger, primary_key=True, nullable=False, autoincrement=True),
        Column("codigo", Uuid(as_uuid=True), nullable=False,server_default=text("gen_random_uuid()"), unique=True),
        Column("anulado", Boolean,server_default=text("false"), nullable=False),
        Column("creado_por", Uuid(as_uuid=True), nullable=False),
        Column("fecha_creacion", DateTime, server_default=func.now(), nullable=False),
        Column("editado_por", Uuid(as_uuid=True), nullable=True),
        Column("fecha_editado", DateTime,onupdate=func.now(), nullable=True),
        Column("pcid", String(150), nullable=False)
    ]
    
    return columnas

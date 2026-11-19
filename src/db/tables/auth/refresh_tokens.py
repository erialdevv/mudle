from sqlalchemy import (
    Table,
    Column,
    String,
    Uuid,
    DateTime,
    func,
    Boolean,
    ForeignKey,
    text,
    BigInteger
)

from db.base_columns import metadata

refresh_tokens = Table(
    "refresh_tokens",
    metadata,
    Column("id", Uuid(as_uuid=True), primary_key=True, nullable=False),
    Column("usuario_id",BigInteger, ForeignKey("sis_usuarios.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("fecha_expiracion", DateTime(timezone=True), nullable=False),
    Column("anulado", Boolean, server_default=text("false"), nullable=False),
    Column("reemplazado_por", Uuid(as_uuid=True), nullable=True), # Opcional, para rotación de tokens
    Column("pcid", String(150), nullable=True),
    Column("fecha_creacion", DateTime(timezone=True), server_default=func.now(), nullable=False),
)

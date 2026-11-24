"""Catálogo de errores de la aplicación.
"""


class AppError(Exception):
    """Error controlado. Cada subclase fija su código HTTP."""

    status_code: int = 500
    default_msg: str = "Ocurrió un error interno al procesar la solicitud."

    def __init__(self, msg: str | None = None, *, field: str | None = None):
        self.msg = msg or self.default_msg
        self.field = field  # Solo para 422: nombre del campo con error
        super().__init__(self.msg)


class BadRequestError(AppError):
    status_code = 400
    default_msg = "Solicitud incorrecta."


class UnauthorizedError(AppError):
    status_code = 401
    default_msg = "No autenticado o token inválido/expirado."


class ForbiddenError(AppError):
    status_code = 403
    default_msg = "Sin permisos."


class NotFoundError(AppError):
    status_code = 404
    default_msg = "Recurso no encontrado."


class ConflictError(AppError):
    status_code = 409
    default_msg = "Conflicto con datos existentes."


class FieldValidationError(AppError):
    """Error de validación asociado a un campo concreto (422)."""

    status_code = 422
    default_msg = "Error de validación."


class InternalError(AppError):
    status_code = 500


class ServiceUnavailableError(AppError):
    status_code = 503
    default_msg = "El servicio no está disponible temporalmente."

import math


def build_page(rows: list[dict] | None, page: int, limit: int) -> tuple[list[dict], dict]:
    """Separa `total_records` (COUNT(*) OVER() de la función SQL) de las filas y arma los metadatos.

    Sin filas devuelve lista vacía y total 0 (un listado vacío no es un error).
    """
    rows = rows or []
    total = int(rows[0]["total_records"]) if rows else 0
    items = [{k: v for k, v in row.items() if k != "total_records"} for row in rows]
    meta = {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": math.ceil(total / limit) if total else 0,
    }
    return items, meta

import re


MAX_ROWS = 2000

FORBIDDEN_SQL = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE|COPY|CALL|DO|MERGE)\b",
    re.IGNORECASE,
)


def validate_read_only_sql(query: str) -> str:
    """Valida y normaliza una consulta SQL de solo lectura."""

    normalized = query.strip()
    if not normalized:
        raise ValueError("La consulta SQL no puede estar vacía.")
    if ";" in normalized:
        raise ValueError("Solo se permite una consulta SQL sin punto y coma.")
    if not re.match(r"^(SELECT|WITH|EXPLAIN)\b", normalized, re.IGNORECASE):
        raise ValueError("Solo se permiten consultas SELECT, WITH o EXPLAIN.")
    if FORBIDDEN_SQL.search(normalized):
        raise ValueError("La consulta contiene una operación SQL no permitida.")
    if "--" in normalized or "/*" in normalized or "*/" in normalized:
        raise ValueError("Los comentarios SQL no están permitidos.")

    if not re.search(r"\bLIMIT\s+\d+\b", normalized, re.IGNORECASE):
        normalized = f"{normalized} LIMIT {MAX_ROWS}"

    return normalized
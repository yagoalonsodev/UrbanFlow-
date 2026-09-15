import re


MAX_ROWS = 2000


FORBIDDEN_SQL = re.compile(
    r"\b("
    r"INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|"
    r"CREATE|GRANT|REVOKE|COPY|CALL|DO|MERGE"
    r")\b",
    re.IGNORECASE,
)


def validate_read_only_sql(query: str) -> str:
    """
    Valida que la consulta sea únicamente de lectura.
    """

    normalized = query.strip()

    if not normalized:
        raise ValueError(
            "La consulta SQL no puede estar vacía."
        )

    if ";" in normalized:
        raise ValueError(
            "Solo se permite una consulta SQL sin punto y coma."
        )

    if not re.match(
        r"^SELECT\b",
        normalized,
        re.IGNORECASE,
    ):
        raise ValueError(
            "Solo se permiten consultas SELECT."
        )

    if FORBIDDEN_SQL.search(normalized):
        raise ValueError(
            "La consulta contiene una operación SQL no permitida."
        )

    if "--" in normalized:
        raise ValueError(
            "Los comentarios SQL no están permitidos."
        )

    if "/*" in normalized or "*/" in normalized:
        raise ValueError(
            "Los comentarios SQL no están permitidos."
        )

    if not re.search(
        r"\bLIMIT\s+\d+\b",
        normalized,
        re.IGNORECASE,
    ):
        normalized = (
            f"{normalized} LIMIT {MAX_ROWS}"
        )

    return normalized
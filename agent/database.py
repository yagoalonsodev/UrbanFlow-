import json
import os
import re
from collections.abc import Sequence

from sqlalchemy import create_engine, text

from agent.guardrails import validate_read_only_sql


TABLE_PATTERN = re.compile(
    r"\b(?:FROM|JOIN)\s+([a-zA-Z_][\w.]*)",
    re.IGNORECASE,
)


def database_url() -> str:
    """
    Obtiene la URL de PostgreSQL.
    """

    return os.getenv(
        "AGENT_DATABASE_URL",
        "postgresql+psycopg2://"
        "urbanflow:urbanflow123@localhost:5432/urbanflow",
    )


def create_database_engine():
    """
    Crea una conexión SQLAlchemy con PostgreSQL.
    """

    return create_engine(
        database_url(),
        pool_pre_ping=True,
    )


def allowed_tables() -> set[str]:
    """
    Devuelve las tablas existentes en el esquema public.
    """

    engine = create_database_engine()

    try:
        with engine.connect() as connection:
            rows = connection.execute(
                text(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    """
                )
            )

            return {
                row[0]
                for row in rows
            }

    finally:
        engine.dispose()


def validate_tables(
    query: str,
    tables: set[str],
) -> None:
    """
    Comprueba que las tablas utilizadas
    en la consulta existen.
    """

    referenced = {
        match.split(".")[-1]
        for match in TABLE_PATTERN.findall(query)
    }

    unknown = referenced - tables

    if unknown:
        raise ValueError(
            "La consulta referencia tablas "
            f"inexistentes: {sorted(unknown)}"
        )


def execute_read_only_sql(
    query: str,
) -> str:
    """
    Ejecuta únicamente SQL de lectura.
    """

    safe_query = validate_read_only_sql(query)

    validate_tables(
        safe_query,
        allowed_tables(),
    )

    engine = create_database_engine()

    try:
        with engine.connect() as connection:

            result = connection.execute(
                text(safe_query)
            )

            columns = list(
                result.keys()
            )

            rows: Sequence[dict] = [
                dict(row._mapping)
                for row in result
            ]

            return json.dumps(
                {
                    "query": safe_query,
                    "columns": columns,
                    "rows": rows,
                },
                default=str,
                ensure_ascii=False,
            )

    finally:
        engine.dispose()


def live_database_context() -> str:
    """
    Obtiene información básica actual
    de la base de datos.
    """

    engine = create_database_engine()

    try:
        with engine.connect() as connection:

            tables = connection.execute(
                text(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                    """
                )
            ).scalars().all()

            snapshots = connection.execute(
                text(
                    """
                    SELECT
                        MAX(snapshot_date)
                            AS latest_snapshot,
                        COUNT(*)
                            AS trips
                    FROM trips
                    """
                )
            ).mappings().one()

            realtime = connection.execute(
                text(
                    """
                    SELECT COUNT(*) AS arrivals
                    FROM realtime_bus_arrivals
                    """
                )
            ).mappings().one()

            return json.dumps(
                {
                    "tables": list(tables),
                    "latest_snapshot": str(
                        snapshots["latest_snapshot"]
                    ),
                    "trips_in_latest_table":
                        snapshots["trips"],
                    "realtime_arrivals":
                        realtime["arrivals"],
                },
                ensure_ascii=False,
            )

    finally:
        engine.dispose()
import sqlite3
import math
import pandas as pd
import json
from pathlib import Path
from typing import Optional


def _sanitize_rows(rows: list[dict]) -> list[dict]:
    """Replace NaN/Inf float values with None for JSON serialization."""
    for row in rows:
        for k, v in row.items():
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                row[k] = None
    return rows

DB_PATH = Path(__file__).parent / "sample_data.db"
UPLOAD_DB_PATH = Path(__file__).parent / "upload.db"


def get_schema_with_samples(db_path: Path, max_sample_rows: int = 3) -> str:
    """
    Returns a rich schema string for injection into the Claude system prompt.
    Format:
      TABLE: table_name
      COLUMNS: col1 (TYPE), col2 (TYPE), ...
      SAMPLE ROWS:
        | col1 | col2 | ...
        | val  | val  | ...
      FOREIGN KEYS: ...
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in c.fetchall()]

    schema_parts = []
    for table in tables:
        c.execute(f"PRAGMA table_info({table})")
        cols = c.fetchall()
        col_defs = ", ".join(f"{col[1]} ({col[2]})" for col in cols)

        c.execute(f"PRAGMA foreign_key_list({table})")
        fks = c.fetchall()
        fk_str = ""
        if fks:
            fk_parts = [f"{fk[3]} -> {fk[2]}.{fk[4]}" for fk in fks]
            fk_str = f"\n  FOREIGN KEYS: {', '.join(fk_parts)}"

        try:
            df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT {max_sample_rows}", conn)
            rows_md = df.to_markdown(index=False)
            sample_str = f"\n  SAMPLE ROWS:\n{rows_md}"
        except Exception:
            sample_str = ""

        schema_parts.append(
            f"TABLE: {table}\n  COLUMNS: {col_defs}{fk_str}{sample_str}"
        )

    conn.close()
    return "\n\n".join(schema_parts)


def execute_sql(db_path: Path, sql: str) -> dict:
    """
    Execute a SQL query and return results as a dict with keys:
      - columns: list of column names
      - rows: list of row dicts
      - row_count: int
      - error: str or None
    """
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        rows = _sanitize_rows(df.to_dict(orient="records"))
        return {
            "columns": list(df.columns),
            "rows": rows,
            "row_count": len(df),
            "error": None
        }
    except Exception as e:
        return {
            "columns": [],
            "rows": [],
            "row_count": 0,
            "error": str(e)
        }


def ingest_csv(csv_path: Path, table_name: str = "uploaded_data") -> dict:
    """
    Load a CSV into the upload SQLite database.
    Auto-detects types. Returns schema info.
    """
    # Skip comment/metadata lines at the top (starting with #)
    skip_rows = 0
    with open(csv_path, "r", errors="replace") as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("#") or stripped == "":
                skip_rows += 1
            else:
                break
    df = pd.read_csv(csv_path, skiprows=skip_rows)
    # Drop fully empty columns
    df = df.dropna(axis=1, how="all")
    df.columns = [
        c.strip().lower().replace(" ", "_").replace("-", "_").replace("/", "_").replace("(", "").replace(")", "").replace("#", "").replace(":", "").lstrip("_")
        for c in df.columns
    ]
    for col in df.columns:
        if "date" in col or "time" in col:
            try:
                df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")
            except Exception:
                pass

    conn = sqlite3.connect(UPLOAD_DB_PATH)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()
    return {
        "table_name": table_name,
        "rows_loaded": len(df),
        "columns": list(df.columns)
    }


def get_active_db() -> Path:
    """Returns the currently active DB path."""
    if UPLOAD_DB_PATH.exists():
        return UPLOAD_DB_PATH
    return DB_PATH

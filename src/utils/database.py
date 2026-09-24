"""
Database Manager module for PostgreSQL and fallback SQLite support.
Provides high-performance connections, table schema management, and batch operations.
"""
import os
import sqlite3
import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Connection
from src.utils.logging import get_logger
from src.utils.config import BASE_DIR

logger = get_logger("database_manager")

def _sqlite_extract_dow(date_str: Optional[str]) -> Optional[int]:
    """PostgreSQL DOW equivalent: 0=Sunday, 1=Monday, ..., 6=Saturday"""
    if not date_str:
        return None
    try:
        # handle date or string
        if isinstance(date_str, (datetime.date, datetime.datetime)):
            d = date_str
        else:
            d = datetime.datetime.strptime(str(date_str)[:10], "%Y-%m-%d").date()
        # python weekday(): 0=Mon..6=Sun -> Postgres DOW: (d.weekday() + 1) % 7
        return (d.weekday() + 1) % 7
    except Exception:
        return None

def _sqlite_extract_hour(time_str: Optional[str]) -> Optional[int]:
    """Extract hour from time string HH:MM:SS"""
    if not time_str:
        return None
    try:
        if isinstance(time_str, datetime.time):
            return time_str.hour
        elif isinstance(time_str, datetime.datetime):
            return time_str.hour
        parts = str(time_str).split(":")
        return int(parts[0])
    except Exception:
        return None

def _sqlite_mod(a: Optional[float], b: Optional[float]) -> Optional[float]:
    if a is None or b is None or b == 0:
        return None
    return float(a) % float(b)

class DatabaseManager:
    """
    Manages database connections, schema execution, and fast data ingestion.
    """
    def __init__(self, force_sqlite: bool = False, db_path: Optional[str] = None):
        self.force_sqlite = force_sqlite
        self.db_path = db_path or os.getenv("SQLITE_DB_PATH", "data/journal_audit.db")
        self.is_sqlite = False
        self.engine: Optional[Engine] = None
        self._init_engine()

    def _init_engine(self):
        """Initializes PostgreSQL or SQLite engine based on environment and availability."""
        if not self.force_sqlite:
            db_user = os.getenv("DB_USER", "audit_user")
            db_pass = os.getenv("DB_PASSWORD", "audit_secure_password_2026")
            db_host = os.getenv("DB_HOST", "localhost")
            db_port = os.getenv("DB_PORT", "5432")
            db_name = os.getenv("DB_NAME", "journal_audit_db")
            
            pg_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
            
            try:
                engine = create_engine(pg_url, pool_pre_ping=True, connect_args={"connect_timeout": 3})
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1;"))
                self.engine = engine
                self.is_sqlite = False
                logger.info(f"Connected to PostgreSQL at {db_host}:{db_port}/{db_name}")
                return
            except Exception as e:
                logger.warning(f"PostgreSQL connection to {db_host}:{db_port} unavailable: {e}")
                
        # Fallback to SQLite
        sqlite_file = BASE_DIR / self.db_path
        sqlite_file.parent.mkdir(parents=True, exist_ok=True)
        sqlite_url = f"sqlite:///{sqlite_file.as_posix()}"
        
        self.engine = create_engine(
            sqlite_url,
            connect_args={"check_same_thread": False}
        )
        self.is_sqlite = True
        logger.info(f"Using SQLite database engine at {sqlite_file}")

    def get_connection(self) -> Connection:
        """Returns an active SQLAlchemy connection."""
        if self.engine is None:
            self._init_engine()
        conn = self.engine.connect()
        if self.is_sqlite:
            # Register SQLite custom helper functions on raw connection
            raw_conn = conn.connection.dbapi_connection
            raw_conn.create_function("EXTRACT_DOW", 1, _sqlite_extract_dow)
            raw_conn.create_function("EXTRACT_HOUR", 1, _sqlite_extract_hour)
            raw_conn.create_function("MOD", 2, _sqlite_mod)
        return conn

    def init_schema(self, schema_file: Optional[Path] = None):
        """Executes database schema script."""
        schema_path = schema_file or (BASE_DIR / "database" / "schema.sql")
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found at {schema_path}")
            
        with open(schema_path, "r", encoding="utf-8") as f:
            sql_content = f.read()

        logger.info(f"Initializing database schema from {schema_path.name}...")
        
        if self.is_sqlite:
            # Adapt schema statements for SQLite
            statements = [
                s.strip() for s in sql_content.split(";") 
                if s.strip() and not s.strip().startswith("--")
            ]
            with self.get_connection() as conn:
                for stmt in statements:
                    # Replace postgres-specific types
                    s = stmt.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
                    s = s.replace("CASCADE", "")
                    s = s.replace("CURRENT_TIMESTAMP", "CURRENT_TIMESTAMP")
                    try:
                        conn.execute(text(s))
                    except Exception as e:
                        logger.debug(f"Statement executed with notice: {e}")
                conn.commit()
        else:
            with self.get_connection() as conn:
                conn.execute(text(sql_content))
                conn.commit()
                
        logger.info("Database schema initialized successfully.")

    def seed_reference_data(self, seed_file: Optional[Path] = None):
        """Seeds reference tables with baseline accounts, departments, and approval rules."""
        seed_path = seed_file or (BASE_DIR / "database" / "seed_reference_data.sql")
        if not seed_path.exists():
            raise FileNotFoundError(f"Seed file not found at {seed_path}")
            
        with open(seed_path, "r", encoding="utf-8") as f:
            sql_content = f.read()

        logger.info(f"Seeding reference data from {seed_path.name}...")
        
        with self.get_connection() as conn:
            if self.is_sqlite:
                # SQLite ON CONFLICT IGNORE
                adapted_sql = sql_content.replace("ON CONFLICT (department_id) DO NOTHING", "ON CONFLICT (department_id) DO NOTHING")
                adapted_sql = adapted_sql.replace("ON CONFLICT (account_code) DO NOTHING", "ON CONFLICT (account_code) DO NOTHING")
                adapted_sql = adapted_sql.replace("ON CONFLICT (rule_id) DO NOTHING", "ON CONFLICT (rule_id) DO NOTHING")
                adapted_sql = adapted_sql.replace("ON CONFLICT (holiday_date) DO NOTHING", "ON CONFLICT (holiday_date) DO NOTHING")
                statements = [s.strip() for s in adapted_sql.split(";") if s.strip() and not s.strip().startswith("--")]
                for stmt in statements:
                    conn.execute(text(stmt))
            else:
                conn.execute(text(sql_content))
            conn.commit()
            
        logger.info("Reference data seeded successfully.")

    def bulk_insert_df(self, table_name: str, df: pd.DataFrame, chunksize: int = 10000):
        """
        Inserts DataFrame into database in high-performance chunks.
        """
        if df.empty:
            logger.warning(f"No records to insert into table '{table_name}'.")
            return
            
        logger.info(f"Bulk inserting {len(df):,} rows into '{table_name}' in batches of {chunksize:,}...")
        df.to_sql(
            name=table_name,
            con=self.engine,
            if_exists="append",
            index=False,
            chunksize=chunksize,
            method="multi" if not self.is_sqlite else None
        )
        logger.info(f"Successfully inserted {len(df):,} rows into '{table_name}'.")

    def query_to_df(self, sql: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Executes SQL query and returns results as pandas DataFrame."""
        with self.get_connection() as conn:
            return pd.read_sql(text(sql), conn, params=params)

    def execute_sql(self, sql: str, params: Optional[Dict[str, Any]] = None):
        """Executes a single SQL statement or command."""
        with self.get_connection() as conn:
            conn.execute(text(sql), params or {})
            conn.commit()

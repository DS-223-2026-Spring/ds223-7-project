import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST",     "db"),
    "port":     int(os.getenv("DB_PORT", "5432")),
    "dbname":   os.getenv("DB_NAME",     "pulse"),
    "user":     os.getenv("DB_USER",     "pulse_user"),
    "password": os.getenv("DB_PASSWORD", "pulse_pass"),
}

def get_connection():
    """
    Create and return a new psycopg2 connection to the database.

    Returns:
        psycopg2.connection: An open database connection.
    """
    return psycopg2.connect(**DB_CONFIG)


def insert(table: str, data: dict) -> None:
    """
    Insert a single row into the specified table.

    Parameters:
        table (str): The name of the table to insert into.
        data (dict): A dictionary mapping column names to values.

    Returns:
        None
    """
    cols = ", ".join(data.keys())
    placeholders = ", ".join(["%s"] * len(data))
    query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, list(data.values()))
        conn.commit()


def select(table: str, filters: dict = None) -> list:
    """
    Select rows from the specified table with optional filters.

    Parameters:
        table (str): The name of the table to query.
        filters (dict, optional): Column-value pairs to filter by (WHERE clause).
                                  If None or empty, all rows are returned.

    Returns:
        list[dict]: A list of rows as dictionaries.
    """
    query = f"SELECT * FROM {table}"
    values = []
    if filters:
        conditions = " AND ".join([f"{col} = %s" for col in filters])
        query += f" WHERE {conditions}"
        values = list(filters.values())
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, values)
            return [dict(row) for row in cur.fetchall()]


def update(table: str, filters: dict, data: dict) -> None:
    """
    Update rows in the specified table that match the given filters.

    Parameters:
        table (str): The name of the table to update.
        filters (dict): Column-value pairs to identify which rows to update.
        data (dict): Column-value pairs with the new values to set.

    Returns:
        None
    """
    set_clause = ", ".join([f"{col} = %s" for col in data])
    where_clause = " AND ".join([f"{col} = %s" for col in filters])
    query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
    values = list(data.values()) + list(filters.values())
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, values)
        conn.commit()


def delete(table: str, filters: dict) -> None:
    """
    Delete rows from the specified table that match the given filters.

    Parameters:
        table (str): The name of the table to delete from.
        filters (dict): Column-value pairs to identify which rows to delete.

    Returns:
        None
    """
    where_clause = " AND ".join([f"{col} = %s" for col in filters])
    query = f"DELETE FROM {table} WHERE {where_clause}"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, list(filters.values()))
        conn.commit()
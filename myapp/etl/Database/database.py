"""
Database utility module for the Pulse platform.

Provides a connection factory and reusable CRUD helpers used by the
ETL pipeline, backend API, and data science workflows.
"""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Connection configuration
# ---------------------------------------------------------------------------

DB_CONFIG = {
    "host":     os.getenv("DB_HOST",     "db"),
    "port":     int(os.getenv("DB_PORT", "5432")),
    "dbname":   os.getenv("DB_NAME",     "pulse"),
    "user":     os.getenv("DB_USER",     "pulse_user"),
    "password": os.getenv("DB_PASSWORD", "pulse_pass"),
}


def get_connection():
    """
    Create and return a new psycopg2 connection using DB_CONFIG.

    Returns:
        psycopg2.connection: An open database connection.

    Raises:
        psycopg2.OperationalError: If the connection cannot be established.
    """
    return psycopg2.connect(**DB_CONFIG)


# ---------------------------------------------------------------------------
# Generic CRUD helpers
# ---------------------------------------------------------------------------

def insert(table: str, data: dict) -> None:
    """
    Insert a single row into the specified table.

    Parameters:
        table (str): Target table name.
        data (dict): Column-value pairs to insert.

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
    Select rows from a table with optional filters.

    Parameters:
        table (str): Table to query.
        filters (dict, optional): Column-value pairs for WHERE clause.

    Returns:
        list[dict]: Matching rows as dictionaries.
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
    Update rows matching the filters with new values.

    Parameters:
        table (str): Table to update.
        filters (dict): WHERE clause column-value pairs.
        data (dict): New column-value pairs to set.

    Returns:
        None
    """
    set_clause   = ", ".join([f"{col} = %s" for col in data])
    where_clause = " AND ".join([f"{col} = %s" for col in filters])
    query  = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
    values = list(data.values()) + list(filters.values())
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, values)
        conn.commit()


def delete(table: str, filters: dict) -> None:
    """
    Delete rows matching the filters.

    Parameters:
        table (str): Table to delete from.
        filters (dict): WHERE clause column-value pairs.

    Returns:
        None
    """
    where_clause = " AND ".join([f"{col} = %s" for col in filters])
    query = f"DELETE FROM {table} WHERE {where_clause}"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, list(filters.values()))
        conn.commit()


# ---------------------------------------------------------------------------
# Business-logic helpers
# ---------------------------------------------------------------------------

def get_user_by_segment(segment_name: str) -> list:
    """
    Return all active users assigned to a named segment.

    Parameters:
        segment_name (str): One of 'power', 'growing', 'casual', 'dormant'.

    Returns:
        list[dict]: User rows belonging to that segment.
    """
    query = """
        SELECT u.*
        FROM users u
        JOIN user_segments us ON us.user_id    = u.user_id
        JOIN segments      s  ON s.segment_id  = us.segment_id
        WHERE s.name = %s AND us.expires_at IS NULL
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, [segment_name])
            return [dict(row) for row in cur.fetchall()]


def update_user_status(user_id: str, new_status: str) -> None:
    """
    Update the account status of a single user.

    Parameters:
        user_id (str): UUID of the user.
        new_status (str): New status — 'active', 'inactive', or 'banned'.

    Returns:
        None
    """
    update("users", filters={"user_id": user_id}, data={"status": new_status})


def get_campaign_by_id(campaign_id: str) -> dict | None:
    """
    Fetch a single campaign row by primary key.

    Parameters:
        campaign_id (str): UUID of the campaign.

    Returns:
        dict: Campaign row, or None if not found.
    """
    results = select("campaigns", filters={"campaign_id": campaign_id})
    return results[0] if results else None


def get_active_message_for_campaign(campaign_id: str) -> dict | None:
    """
    Return the active message template for a campaign.

    Parameters:
        campaign_id (str): UUID of the campaign.

    Returns:
        dict: Active message template row, or None if not found.
    """
    results = select("message_templates", filters={
        "campaign_id": campaign_id,
        "is_active":   True,
    })
    return results[0] if results else None


def get_users_by_plan(plan: str) -> list:
    """
    Return all users on a specific subscription plan.

    Parameters:
        plan (str): Plan type — 'free', 'pro', or 'cancelled'.

    Returns:
        list[dict]: User rows on that plan.
    """
    return select("users", filters={"plan": plan})
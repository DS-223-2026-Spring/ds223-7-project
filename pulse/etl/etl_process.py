"""ETL entry point — runs connection check then seeds all CSV data."""
from check_connection import check_connection, verify_tables, verify_seed_data
from seed_flat_data import main as seed_main

if __name__ == "__main__":
    conn = check_connection()
    verify_tables(conn)
    verify_seed_data(conn)
    conn.close()
    seed_main()

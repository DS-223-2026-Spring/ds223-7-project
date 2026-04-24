"""ETL entry point — verifies DB connection/tables then seeds all data."""
from check_connection import check_connection, verify_tables, verify_seed_data
from seed_flat_data import main as seed_main

if __name__ == "__main__":
    print("=" * 50)
    print("Pulse ETL — starting")
    print("=" * 50)

    conn = check_connection()
    verify_tables(conn)
    verify_seed_data(conn)
    conn.close()

    seed_main()

    print("=" * 50)
    print("Pulse ETL — complete")
    print("=" * 50)

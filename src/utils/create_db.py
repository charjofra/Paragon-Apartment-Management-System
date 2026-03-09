from utils.db_utils import get_db_connection
from config import DB_CONFIG


def _database_exists(cursor, db_name: str) -> bool:
    """Check whether the target database already exists on the server."""
    cursor.execute("SHOW DATABASES LIKE %s", (db_name,))
    return cursor.fetchone() is not None


def create_database() -> None:
    """Creates the database and tables only if they don't already exist."""

    db_name = DB_CONFIG.get("database", "paragon_apartment_management_system")

    # Connect to the MySQL server (NOT the specific database yet)
    conn = get_db_connection(connect_to_db=False)

    if not conn:
        print("Failed to start database creation process.")
        return

    try:
        db_cursor = conn.cursor()

        # Skip entirely if the database already exists
        if _database_exists(db_cursor, db_name):
            print(f"Database '{db_name}' already exists — skipping schema creation.")
            return

        # Read the schema file
        with open('db/schema.sql', 'r') as f:
            sql_script = f.read()

        # Execute each statement one by one
        for statement in sql_script.split(';'):
            if statement.strip():
                db_cursor.execute(statement)

        conn.commit()
        print("Database and schema initialized successfully!")

    except Exception as e:
        print(f"An error occurred while running schema.sql: {e}")

    finally:
        db_cursor.close()
        conn.close()
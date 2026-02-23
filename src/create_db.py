from db_utils import get_db_connection

def create_database() -> None:
    """ Creates the database and tables if they don't exist, should be idempotent. """
    
    # Connect to the MySQL server (NOT the specific database yet)
    conn = get_db_connection(connect_to_db=False)
    
    # If connection failed, get_db_connection already printed the error
    if not conn:
        print("Failed to start database creation process.")
        return

    try:
        db_cursor = conn.cursor()
        
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
        # If any error occurs during the execution of the SQL script, print it out.
        print(f"An error occurred while running schema.sql: {e}")
        
    finally:
        db_cursor.close()
        conn.close()
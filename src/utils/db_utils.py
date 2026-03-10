from config import DB_CONFIG
import mysql.connector

def get_db_connection(connect_to_db: bool = True) -> mysql.connector.connection.MySQLConnection | None:
    """ Attempts to establish a connection to the MySQL database. """
    
    config_to_use = DB_CONFIG.copy()
    
    # If creating the DB, remove the database name from the connection attempt
    if not connect_to_db:
        config_to_use.pop("database", None)

    try:
        connection = mysql.connector.connect(**config_to_use)
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

def execute_read(query: str, params: tuple = None) -> list:
    """ Executes a read (SELECT) query and returns the results as a list of dictionaries. """
    
    conn = get_db_connection()
    if conn is None:
        raise Exception("Failed to connect to database. Check your .env credentials.")
    
    try:
        cursor = conn.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        return cursor.fetchall()
    
    finally:
        conn.close()

def execute_write(query: str, params: tuple = None) -> int:
    """ Executes a write (INSERT/UPDATE/DELETE) query, returns the last inserted ID for INSERTs or number of affected rows for UPDATE/DELETE. """
    
    conn = get_db_connection()
    if conn is None:
        raise Exception("Failed to connect to database. Check your .env credentials.")
    
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        conn.commit()
        return cursor.lastrowid
    
    finally:
        conn.close()
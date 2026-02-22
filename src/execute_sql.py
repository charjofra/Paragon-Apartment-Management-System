from config import get_db_connection

def execute_read(query: str, params: tuple = None) -> list:
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
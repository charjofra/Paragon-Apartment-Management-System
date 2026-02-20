import mysql.connector
from mysql.connector import errorcode
import config

def create_database() -> mysql.connector.connection.MySQLConnection:
    try:
        conn = mysql.connector.connect(host=config.DB_HOST,
                                       user=config.DB_USER,
                                       password=config.DB_PASSWORD)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("username or password invalid")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("database does not exist")
        else:
            print(err)
    else:
        if conn.is_connected():
            print("MySQL connection established")
    
        db_cursor = conn.cursor()
        
        with open('db/schema.sql', 'r') as f:
            sql_script = f.read()

        for statement in sql_script.split(';'):
            if statement.strip():
                db_cursor.execute(statement)
                
        conn.commit()
        db_cursor.close()
        conn.close()

import mysql.connector
import os
from mysql.connector import Error
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.environ.get("MYSQLHOST"),
            user=os.environ.get("MYSQLUSER"),
            password=os.environ.get("MYSQLPASSWORD"),
            database=os.environ.get("MYSQLDATABASE"),
            port=int(os.environ.get("MYSQLPORT")),
            autocommit=True,
            connection_timeout=30
        )
        cursor = conn.cursor(dictionary=True)
        return conn, cursor
    except Error as e:
        print(f"MySQL Connection Error: {e}")
        return None, None
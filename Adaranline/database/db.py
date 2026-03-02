import mysql.connector
import os
from mysql.connector import Error
try:
    conn = mysql.connector.connect(
    host=os.environ.get("MYSQL_HOST"),
    user=os.environ.get("MYSQL_USER"),
    password=os.environ.get("MYSQL_PASSWORD"),
    database=os.environ.get("MYSQL_DATABASE"),
    port=int(os.environ.get("MYSQL_PORT"))
)
    cursor=conn.cursor(dictionary=True)
    conn.autocommit=True
    print("Database Connected Successfully")
except Error as e:
    print(f"error conneting to my sql {e}")
    conn=None
    cursor=None

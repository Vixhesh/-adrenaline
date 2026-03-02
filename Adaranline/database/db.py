import mysql.connector
import os
from mysql.connector import Error
try:
    conn = mysql.connector.connect(
    host=os.environ.get("MYSQLHOST"),
    user=os.environ.get("MYSQLUSER"),
    password=os.environ.get("MYSQLPASSWORD"),
    database=os.environ.get("MYSQLDATABASE"),
    port=int(os.environ.get("MYSQLPORT"))
)
    cursor=conn.cursor(dictionary=True)
    conn.autocommit=True
    print("Database Connected Successfully")
except Error as e:
    print(f"error conneting to my sql {e}")
    conn=None
    cursor=None
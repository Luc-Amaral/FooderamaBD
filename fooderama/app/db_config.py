import mysql.connector
import os

def get_db_connection():
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST', '127.0.0.1'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'root'),
        database=os.getenv('DB_NAME', 'fooderama'),
        port=int(os.getenv('DB_PORT', 3306))
    )
    return connection
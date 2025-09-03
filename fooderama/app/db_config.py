import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='angryjam123',
        database='fooderama'
    )
    return connection

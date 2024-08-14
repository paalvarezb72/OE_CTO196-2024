# utils/db_connection.py
import prestodb

def create_connection():
    conn = prestodb.dbapi.connect(
        host='172.16.50.20',
        port=8080,
        user='Paola',
        catalog='raw',
        schema='cassandra',
    )
    cur = conn.cursor()
    return conn, cur
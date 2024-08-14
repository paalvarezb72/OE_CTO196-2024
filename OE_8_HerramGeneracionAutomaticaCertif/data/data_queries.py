# data/data_queries.py
from utils.db_connection import create_connection

def fetch_data(query):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    return data

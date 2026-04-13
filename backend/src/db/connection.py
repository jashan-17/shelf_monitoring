import psycopg2

def get_connection():
    conn = psycopg2.connect(
        host = "localhost",
        database = "shelf_monitoring",
        user = "postgres",
        password = "root1704",
        port = "5432"
    )

    return conn


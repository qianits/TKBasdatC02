from django.db import connection, DatabaseError, IntegrityError
from collections import namedtuple
import psycopg2
from psycopg2 import Error
from psycopg2.extras import RealDictCursor

try:
    connection = psycopg2.connect(
            host="containers-us-west-16.railway.app",
            database="railway",
            user="postgres",
            password="sy1E0k72n02YUrWqURGM",
            port="6667"
        )
    connection.autocommit = True
    cursor = connection.cursor()

except (Exception, Error) as error:
    print("Error while connectiong to PostgreSQL", error)

def map_cursor(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple("Result", [col[0] for col in desc])
    return [dict(row) for row in cursor.fetchall()]


def query(query_str: str):
    hasil = []
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SET SEARCH_PATH TO ULEAGUE")
        try:
            cursor.execute(query_str)

            if query_str.strip().lower().startswith("select"):
                # Kalau ga error, return hasil SELECT
                hasil = map_cursor(cursor)
            else:
                # Kalau ga error, return jumlah row yang termodifikasi oleh INSERT, UPDATE, DELETE
                hasil = cursor.rowcount
        except Exception as e:
            # Ga tau error apa
            hasil = e
    return hasil


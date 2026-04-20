import psycopg2.extras

from src.db.connection import get_connection


def _dict_cursor():
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    return connection, cursor


def insert_single_prediction(image_name, predicted_label, confidence, actual_label=None):
    connection, cursor = _dict_cursor()
    try:
        cursor.execute(
            """
            INSERT INTO raw_predictions (image_name, actual_label, predicted_label, confidence)
            VALUES (%s, %s, %s, %s)
            RETURNING id, image_name, actual_label, predicted_label, confidence, created_at
            """,
            (image_name, actual_label, predicted_label, confidence),
        )
        row = cursor.fetchone()
        connection.commit()
        return {**row, "confidence": round(float(row["confidence"]), 4)}
    finally:
        cursor.close()
        connection.close()

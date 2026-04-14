from collections import defaultdict

import psycopg2.extras

from src.db.connection import get_connection

CLASS_NAMES = ["empty", "low", "medium", "full"]


def _dict_cursor():
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    return connection, cursor


def fetch_summary():
    connection, cursor = _dict_cursor()
    try:
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_predictions,
                COALESCE(AVG(confidence), 0) AS average_confidence
            FROM raw_predictions
            """
        )
        overview = cursor.fetchone()

        cursor.execute(
            """
            SELECT predicted_label, COUNT(*) AS total
            FROM raw_predictions
            GROUP BY predicted_label
            """
        )
        counts = {label: 0 for label in CLASS_NAMES}
        for row in cursor.fetchall():
            label = row["predicted_label"]
            if label in counts:
                counts[label] = int(row["total"])

        return {
            "total_predictions": int(overview["total_predictions"] or 0),
            "counts_by_class": counts,
            "average_confidence": round(float(overview["average_confidence"] or 0), 4),
        }
    finally:
        cursor.close()
        connection.close()


def fetch_latest_predictions(limit=10):
    connection, cursor = _dict_cursor()
    try:
        cursor.execute(
            """
            SELECT id, image_name, actual_label, predicted_label, confidence, created_at
            FROM raw_predictions
            ORDER BY created_at DESC, id DESC
            LIMIT %s
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        return [
            {
                **row,
                "confidence": round(float(row["confidence"]), 4),
            }
            for row in rows
        ]
    finally:
        cursor.close()
        connection.close()


def fetch_stock_level_analytics():
    connection, cursor = _dict_cursor()
    try:
        cursor.execute(
            """
            SELECT
                predicted_label AS stock_level,
                COUNT(*) AS total_images,
                COALESCE(AVG(confidence), 0) AS avg_confidence
            FROM raw_predictions
            GROUP BY predicted_label
            ORDER BY total_images DESC, predicted_label ASC
            """
        )
        rows = cursor.fetchall()
        return [
            {
                "stock_level": row["stock_level"],
                "total_images": int(row["total_images"]),
                "avg_confidence": round(float(row["avg_confidence"]), 4),
            }
            for row in rows
        ]
    finally:
        cursor.close()
        connection.close()


def fetch_prediction_trends(days=7):
    connection, cursor = _dict_cursor()
    try:
        cursor.execute(
            """
            SELECT
                DATE(created_at) AS prediction_date,
                predicted_label,
                COUNT(*) AS total
            FROM raw_predictions
            WHERE created_at >= CURRENT_DATE - (%s::int - 1)
            GROUP BY DATE(created_at), predicted_label
            ORDER BY prediction_date ASC
            """,
            (days,),
        )
        grouped = defaultdict(lambda: {label: 0 for label in CLASS_NAMES})
        for row in cursor.fetchall():
            grouped[row["prediction_date"].isoformat()][row["predicted_label"]] = int(row["total"])

        return [
            {"date": date_key, **counts}
            for date_key, counts in sorted(grouped.items(), key=lambda item: item[0])
        ]
    finally:
        cursor.close()
        connection.close()


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
        return {
            **row,
            "confidence": round(float(row["confidence"]), 4),
        }
    finally:
        cursor.close()
        connection.close()


def check_database_status():
    connection, cursor = _dict_cursor()
    try:
        cursor.execute("SELECT 1 AS ok")
        cursor.fetchone()
        return True
    finally:
        cursor.close()
        connection.close()

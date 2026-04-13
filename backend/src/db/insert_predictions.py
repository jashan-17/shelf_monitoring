import pandas as pd
from connection import get_connection

def insert_predictions():
    df = pd.read_csv("data/predictions/predictions.csv")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM raw_predictions")

    for _, row in df.iterrows():
        cursor.execute(
                        """
                        INSERT INTO raw_predictions (image_name, actual_label, predicted_label, confidence)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (row["image_name"], row["actual_label"], row["predicted_label"], row["confidence"])
                    )
                        
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    insert_predictions()
    print("Data inserted into PostgreSQL")
import os
import sqlite3
import pandas as pd
import csv

# Specify the desired directory and file name for the database file
DB_DIRECTORY = ''
OLD_DATABASE_FILE = 'feedback_data.db'
DATABASE_FILE = 'new_database.db'
TABLE_NAME = 'feedback'
NEW_TABLE_NAME = 'new_feedback'
OUTPUT_FILE = 'output.csv'

original_conn = sqlite3.connect(os.path.join(DB_DIRECTORY, OLD_DATABASE_FILE))

def delete_uncompleted_entries():
    with original_conn:
        original_conn.execute(f'''
            DELETE FROM {TABLE_NAME}
            WHERE image_name NOT IN (
                SELECT DISTINCT image_name
                FROM {TABLE_NAME}
                WHERE question = 6
            )
        ''')

query = "SELECT * FROM " + TABLE_NAME + " WHERE score != 0"
df = pd.read_sql_query(query, original_conn)
original_conn.close()

pivot_df = pd.pivot_table(df, values=['score', 'comments', 'hard'], index=['image_name', 'question'], columns=['username'], aggfunc='first')

pivot_df.columns = [f'{username}_{metric}' for username, metric in pivot_df.columns]
pivot_df.reset_index(inplace=True)

new_df = pivot_df.copy()

new_conn = sqlite3.connect(os.path.join(DB_DIRECTORY, DATABASE_FILE))

new_df.to_sql(NEW_TABLE_NAME, new_conn, index=False, if_exists='replace')

new_conn.close()
conn = sqlite3.connect(os.path.join(DB_DIRECTORY, DATABASE_FILE))
cursor = conn.cursor()

cursor.execute(f"SELECT * FROM {NEW_TABLE_NAME} ORDER BY image_name ASC")
rows = cursor.fetchall()
columns = [description[0] for description in cursor.description]

with open(OUTPUT_FILE, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(columns)
    csv_writer.writerows(rows)

conn.close()
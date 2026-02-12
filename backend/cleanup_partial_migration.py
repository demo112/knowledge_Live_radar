import sqlite3
import os

DB_PATH = "ai_radar.db"

def cleanup():
    if not os.path.exists(DB_PATH):
        print(f"{DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables_to_drop = [
        "api_metrics",
        "error_records",
        "notification_preferences",
        "notifications",
        "prompt_templates",
        "prompt_versions",
        "ab_tests"
    ]
    
    for table in tables_to_drop:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"Dropped table {table}")
        except Exception as e:
            print(f"Error dropping {table}: {e}")
            
    conn.commit()
    conn.close()
    print("Cleanup complete.")

if __name__ == "__main__":
    cleanup()

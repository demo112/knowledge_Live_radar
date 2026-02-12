import sqlite3
import os

print(f"CWD: {os.getcwd()}")
if os.path.exists("ai_radar.db"):
    print("ai_radar.db exists")
else:
    print("ai_radar.db does NOT exist")

try:
    con = sqlite3.connect("ai_radar.db")
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", tables)
    con.close()
except Exception as e:
    print("Error:", e)

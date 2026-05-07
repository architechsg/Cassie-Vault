"""
Cassie DB Fetcher — fetches ALL tables from MySQL and saves to JSON.
Usage: python fetch_db_data.py
"""
import json
import sys
import os

try:
    import MySQLdb
    import MySQLdb.cursors
    DictCursor = MySQLdb.cursors.DictCursor
except ImportError:
    print("MySQLdb not found. Trying pymysql...")
    try:
        import pymysql as MySQLdb
        import pymysql.cursors
        DictCursor = pymysql.cursors.DictCursor
        MySQLdb.install_as_MySQLdb()
    except ImportError:
        print("Installing pymysql...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pymysql"])
        import pymysql as MySQLdb
        import pymysql.cursors
        DictCursor = pymysql.cursors.DictCursor

DB = dict(
    host="s2.architech.sg",
    port=3306,
    user="weixing_staging",
    password="*6ez0G9d0",
    db="cmlg_staging",
    charset="utf8mb4",
)

def safe_serialize(obj):
    import datetime
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    return str(obj)

def main():
    print("Connecting to database...")
    conn = MySQLdb.connect(**DB)
    cursor = conn.cursor(DictCursor)
    print("Connected!\n")

    out_dir = os.path.dirname(os.path.abspath(__file__))

    # Get all table names
    cursor.execute("SHOW TABLES")
    tables = [list(r.values())[0] for r in cursor.fetchall()]
    print(f"Found {len(tables)} tables: {tables}\n")

    skipped = []
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) as cnt FROM `{table}`")
            count = cursor.fetchone()["cnt"]

            # Skip very large tables (registration/payment records — not needed for chatbot)
            if count > 5000:
                print(f"  SKIPPING {table} ({count} rows — too large, likely transactional)")
                skipped.append((table, count))
                continue

            cursor.execute(f"SELECT * FROM `{table}` LIMIT 500")
            rows = cursor.fetchall()
            out_path = os.path.join(out_dir, f"db_{table}.json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(rows, f, default=safe_serialize, indent=2, ensure_ascii=False)
            print(f"  ✓ {table}: {count} rows → db_{table}.json")
        except Exception as e:
            print(f"  ✗ {table}: ERROR — {e}")

    print("\n--- SKIPPED (large transactional tables) ---")
    for name, cnt in skipped:
        print(f"  {name}: {cnt} rows")

    conn.close()
    print("\nDone! All files saved to:", out_dir)

if __name__ == "__main__":
    main()

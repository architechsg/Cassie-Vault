"""
Cassie DB Fetcher Part 2 — active modules + OLA module_id mapping from Class_Creation.
Usage: python fetch_db_data2.py
"""
import json, sys, os

try:
    import MySQLdb, MySQLdb.cursors
    DictCursor = MySQLdb.cursors.DictCursor
except ImportError:
    import pymysql as MySQLdb, pymysql.cursors
    DictCursor = pymysql.cursors.DictCursor

DB = dict(host="s2.architech.sg", port=3306, user="weixing_staging",
          password="*6ez0G9d0", db="cmlg_staging", charset="utf8mb4")

def safe(obj):
    import datetime
    if isinstance(obj, (datetime.date, datetime.datetime)): return obj.isoformat()
    if isinstance(obj, bytes): return obj.decode("utf-8", errors="replace")
    return str(obj)

def save(name, rows):
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"db2_{name}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rows, f, default=safe, indent=2, ensure_ascii=False)
    print(f"  ✓ {name}: {len(rows)} rows → db2_{name}.json")

conn = MySQLdb.connect(**DB)
cur = conn.cursor(DictCursor)

# 1. KEY: Get OLA module_id mapping via Class_Creation.Module_Prefix_1
# Module_Prefix_1 IS the OLA API module_id integer
print("Fetching OLA module_id mapping from Class_Creation...")
cur.execute("""
    SELECT
        cc.Module_Prefix_1 AS ola_module_id,
        m.Module_Prefix,
        m.ShortName,
        m.Description,
        m.CourseRefNo,
        m.ModuleURL,
        m.ModuleLoc,
        m.Course_Type,
        m.TrainingType,
        m.Full_Fees,
        m.Full_Fees_GST,
        m.MCES_Price,
        m.SingaporePR,
        m.Days,
        m.Hours,
        m.Active,
        a.ATO_Name
    FROM Class_Creation cc
    JOIN Modules m ON cc.Module_Prefix_1 = m.ID
    LEFT JOIN ATO a ON m.ATO1 = a.ID
    WHERE cc.Start_Date >= '2025-01-01'
    GROUP BY cc.Module_Prefix_1, m.Module_Prefix, m.ShortName, m.Description,
             m.CourseRefNo, m.ModuleURL, m.ModuleLoc, m.Course_Type, m.TrainingType,
             m.Full_Fees, m.Full_Fees_GST, m.MCES_Price, m.SingaporePR,
             m.Days, m.Hours, m.Active, a.ATO_Name
    ORDER BY m.Module_Prefix
""")
save("ola_module_mapping", cur.fetchall())

# 2. Active modules with all pricing fields
print("Fetching all active modules...")
cur.execute("""
    SELECT
        m.ID AS ola_module_id,
        m.Module_Prefix,
        m.ShortName,
        m.Description,
        m.CourseRefNo,
        m.Module_Code,
        m.ModuleURL,
        m.ModuleLoc,
        m.Course_Type,
        m.TrainingType,
        m.Full_Fees,
        m.Full_Fees_GST,
        m.MCES_Price,
        m.SingaporePR,
        m.IBFSELF21,
        m.IBFSME21,
        m.IBFSME40,
        m.Days,
        m.Hours,
        m.Timings,
        m.Funding_Period,
        m.Fund_EndDate,
        m.PSEA,
        m.UTAP,
        m.AddSFC,
        m.Remarks,
        m.AssessType,
        a.ATO_Name,
        a.ID as ATO_ID
    FROM Modules m
    LEFT JOIN ATO a ON m.ATO1 = a.ID
    WHERE m.Active = 1
    ORDER BY m.Module_Prefix
""")
save("active_modules_full", cur.fetchall())

# 3. Recent classes to confirm location usage
print("Fetching recent class schedule sample...")
cur.execute("""
    SELECT
        cc.ID,
        cc.Class_Name,
        cc.Start_Date,
        cc.End_Date,
        cc.Day_Start,
        cc.Class_Status,
        cc.Module_Prefix_1 AS ola_module_id,
        m.Module_Prefix,
        m.ShortName,
        l.Location,
        cc.MaxPax
    FROM Class_Creation cc
    JOIN Modules m ON cc.Module_Prefix_1 = m.ID
    JOIN Location l ON cc.Location = l.ID
    WHERE cc.Start_Date >= '2026-01-01'
      AND cc.Class_Status IN ('Scheduled', 'Confirmed', 'Open')
    ORDER BY cc.Start_Date
    LIMIT 100
""")
save("upcoming_classes", cur.fetchall())

conn.close()
print("\nDone! Files saved to:", os.path.dirname(os.path.abspath(__file__)))

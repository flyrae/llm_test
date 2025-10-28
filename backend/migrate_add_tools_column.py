"""
迁移脚本：为test_cases表添加tools列
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "data", "models.db")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查列是否已存在
    cursor.execute("PRAGMA table_info(test_cases)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'tools' not in columns:
        print("Adding 'tools' column to test_cases table...")
        cursor.execute("ALTER TABLE test_cases ADD COLUMN tools JSON")
        conn.commit()
        print("✓ Column 'tools' added successfully!")
    else:
        print("✓ Column 'tools' already exists.")
    
    # 验证
    cursor.execute("PRAGMA table_info(test_cases)")
    print("\nCurrent test_cases table structure:")
    for row in cursor.fetchall():
        print(f"  {row[1]} ({row[2]})")
    
    conn.close()
    print("\n✓ Migration completed successfully!")
    
except Exception as e:
    print(f"✗ Error during migration: {e}")
    if conn:
        conn.rollback()
        conn.close()

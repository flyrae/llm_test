"""
迁移脚本：为test_cases表添加expected_tool_calls列
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
    
    if 'expected_tool_calls' not in columns:
        print("Adding 'expected_tool_calls' column to test_cases table...")
        cursor.execute("ALTER TABLE test_cases ADD COLUMN expected_tool_calls JSON")
        conn.commit()
        print("✓ Column 'expected_tool_calls' added successfully!")
    else:
        print("✓ Column 'expected_tool_calls' already exists.")
    
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

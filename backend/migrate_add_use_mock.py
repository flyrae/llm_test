"""添加 use_mock 字段到 test_cases 表"""
import sqlite3
import os

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "models.db")

def migrate():
    """执行迁移"""
    print("开始迁移：添加 use_mock 字段到 test_cases 表")
    
    # 检查数据库文件是否存在
    if not os.path.exists(DB_PATH):
        print(f"错误：数据库文件不存在: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(test_cases)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'use_mock' in columns:
            print("字段 use_mock 已存在，跳过迁移")
            return
        
        # 添加 use_mock 字段
        print("添加 use_mock 字段...")
        cursor.execute("""
            ALTER TABLE test_cases 
            ADD COLUMN use_mock INTEGER DEFAULT 0
        """)
        
        conn.commit()
        print(f"✅ 迁移完成！")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 迁移失败: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

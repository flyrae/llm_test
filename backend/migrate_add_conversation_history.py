"""
添加 conversation_history 字段到 test_cases 表
用于支持多轮对话测试
"""
import sqlite3
import json

def migrate():
    conn = sqlite3.connect('data/models.db')
    cursor = conn.cursor()
    
    try:
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(test_cases)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'conversation_history' not in columns:
            # 添加 conversation_history 字段
            cursor.execute("""
                ALTER TABLE test_cases 
                ADD COLUMN conversation_history TEXT
            """)
            
            conn.commit()
            print("✅ 成功添加 conversation_history 字段")
            print("📝 说明: 用于存储多轮对话历史，格式为JSON数组")
            print("   示例: [{'role': 'user', 'content': '你好'}, {'role': 'assistant', 'content': '你好！'}]")
        else:
            print("⚠️  conversation_history 字段已存在，跳过迁移")
            
    except Exception as e:
        conn.rollback()
        print(f"❌ 迁移失败: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

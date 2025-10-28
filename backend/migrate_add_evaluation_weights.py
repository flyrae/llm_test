"""
添加 evaluation_weights 字段到 test_cases 表
用于存储自定义的评分权重配置
"""
import sqlite3
import json

def migrate():
    # 使用和应用相同的数据库路径
    db_path = 'data/models.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(test_cases)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'evaluation_weights' not in columns:
            # 添加 evaluation_weights 字段
            cursor.execute("""
                ALTER TABLE test_cases 
                ADD COLUMN evaluation_weights TEXT
            """)
            
            # 为现有记录设置默认权重
            default_weights = json.dumps({
                "tool_calls": 70,      # 工具调用 70%
                "text_similarity": 20, # 文本相似度 20%
                "custom_criteria": 10  # 自定义标准 10%
            })
            
            cursor.execute("""
                UPDATE test_cases 
                SET evaluation_weights = ?
                WHERE evaluation_weights IS NULL
            """, (default_weights,))
            
            conn.commit()
            print("✅ 成功添加 evaluation_weights 字段")
            print(f"✅ 默认权重: 工具调用70%, 文本相似度20%, 自定义标准10%")
        else:
            print("⚠️  evaluation_weights 字段已存在，跳过迁移")
            
    except Exception as e:
        conn.rollback()
        print(f"❌ 迁移失败: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

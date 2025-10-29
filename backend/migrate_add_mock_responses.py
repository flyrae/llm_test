"""添加 mock_responses 字段到 tool_definitions 表"""
import sqlite3
import os
import json

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "models.db")

def migrate():
    """执行迁移"""
    print("开始迁移：添加 mock_responses 字段到 tool_definitions 表")
    
    # 检查数据库文件是否存在
    if not os.path.exists(DB_PATH):
        print(f"错误：数据库文件不存在: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(tool_definitions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'mock_responses' in columns:
            print("字段 mock_responses 已存在，跳过迁移")
            return
        
        # 添加 mock_responses 字段
        print("添加 mock_responses 字段...")
        cursor.execute("""
            ALTER TABLE tool_definitions 
            ADD COLUMN mock_responses TEXT
        """)
        
        # 为现有记录设置默认的 mock_responses 配置
        print("初始化现有工具的默认 mock 配置...")
        cursor.execute("SELECT id, name FROM tool_definitions")
        tools = cursor.fetchall()
        
        for tool_id, tool_name in tools:
            default_mock_config = {
                "enabled": False,
                "response_type": "static",
                "static_response": {
                    "success": True,
                    "data": f"这是 {tool_name} 工具的模拟响应",
                    "message": "模拟执行成功"
                },
                "latency_ms": {
                    "min": 100,
                    "max": 500
                }
            }
            cursor.execute(
                "UPDATE tool_definitions SET mock_responses = ? WHERE id = ?",
                (json.dumps(default_mock_config, ensure_ascii=False), tool_id)
            )
        
        conn.commit()
        print(f"✅ 迁移完成！已更新 {len(tools)} 个工具的 mock 配置")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 迁移失败: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

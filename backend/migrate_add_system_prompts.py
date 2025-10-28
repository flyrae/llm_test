# -*- coding: utf-8 -*-
"""添加系统提示词表"""
import sqlite3
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def migrate():
    """添加系统提示词表"""
    db_path = project_root / "llm_test.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建系统提示词表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            content TEXT NOT NULL,
            category TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 插入一些默认的系统提示词模板
    default_prompts = [
        (
            "General Assistant",
            "You are a friendly and professional AI assistant dedicated to providing accurate and helpful responses.",
            "General",
            "Suitable for general conversation and Q&A scenarios"
        ),
        (
            "Programming Assistant",
            "You are an experienced software engineer proficient in multiple programming languages and frameworks. Your responses should be accurate, concise, and include code examples. Focus on code quality, best practices, and performance optimization.",
            "Programming",
            "Suitable for programming-related questions and code generation"
        ),
        (
            "Translation Assistant",
            "You are a professional translation expert who can accurately understand the meaning of the source language and express it naturally and fluently in the target language. Pay attention to maintaining the tone and style of the original text, and provide cultural background explanations when necessary.",
            "Translation",
            "Suitable for multi-language translation scenarios"
        ),
        (
            "Content Writing",
            "You are a creative copywriting expert skilled in writing engaging marketing copy, articles, and content. Your writing style is vivid and interesting, good at using rhetorical techniques, and can adjust tone and style according to different scenarios.",
            "Writing",
            "Suitable for copywriting and content writing"
        ),
        (
            "Data Analyst",
            "You are a senior data analyst skilled in data processing, statistical analysis, and visualization. You can clearly explain the meaning behind the data and provide insightful analysis conclusions and recommendations.",
            "Data Analysis",
            "Suitable for data analysis and interpretation scenarios"
        ),
        (
            "JSON Expert",
            "You are a JSON format expert. For all questions, you only return valid JSON format data without any additional explanations or markdown formatting.",
            "Formatting",
            "Force JSON format output"
        ),
        (
            "Concise Answer",
            "Your answers should be as concise and clear as possible, hitting the point directly. Avoid lengthy explanations unless the user explicitly requests detailed clarification.",
            "General",
            "Suitable for scenarios requiring quick and concise answers"
        ),
        (
            "Teaching Assistant",
            "You are a patient teacher skilled in explaining complex concepts in simple and easy-to-understand ways. You will use analogies, examples, and step-by-step methods to help users understand.",
            "Education",
            "Suitable for teaching and knowledge explanation scenarios"
        )
    ]
    
    # 插入默认提示词（如果不存在）
    for name, content, category, description in default_prompts:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO system_prompts (name, content, category, description)
                VALUES (?, ?, ?, ?)
            """, (name, content, category, description))
        except Exception as e:
            print(f"Failed to insert default prompt {name}: {e}")
    
    conn.commit()
    conn.close()
    
    print("System prompts table created successfully")
    print(f"Added {len(default_prompts)} default prompt templates")

if __name__ == "__main__":
    migrate()

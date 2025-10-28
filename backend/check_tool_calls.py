# -*- coding: utf-8 -*-
import sqlite3
import json
import os

# Find the correct database file
db_paths = ['data/models.db', 'llm_test.db']

for db_path in db_paths:
    if os.path.exists(db_path):
        print(f'Found database: {db_path}')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f'Tables: {tables}')
        
        if 'test_cases' in tables:
            cursor.execute('SELECT id, title, expected_tool_calls FROM test_cases ORDER BY id DESC LIMIT 5')
            rows = cursor.fetchall()
            
            print('\nRecent 5 test cases:')
            print('=' * 100)
            
            for row in rows:
                id, title, expected_tool_calls = row
                print(f'\nID: {id}')
                print(f'Title: {title}')
                print(f'Expected Tool Calls: ', end='')
                if expected_tool_calls:
                    try:
                        data = json.loads(expected_tool_calls)
                        print(json.dumps(data, ensure_ascii=False, indent=2))
                    except:
                        print(expected_tool_calls)
                else:
                    print('NULL')
                print('-' * 100)
        
        conn.close()
        break
else:
    print('Database not found')

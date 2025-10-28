"""测试工具批量导入API"""
import requests
import json

BASE_URL = "http://localhost:8000"

# 测试数据
test_tools = [
    {
        "name": "test_tool_1",
        "description": "测试工具1",
        "category": "test",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "参数1"
                }
            },
            "required": ["param1"]
        },
        "example_call": {"param1": "value1"},
        "tags": "test,demo"
    },
    {
        "name": "test_tool_2",
        "description": "测试工具2",
        "category": "test",
        "parameters": {
            "type": "object",
            "properties": {
                "param2": {
                    "type": "number",
                    "description": "参数2"
                }
            },
            "required": ["param2"]
        },
        "example_call": {"param2": 123},
        "tags": "test,demo"
    }
]


def test_batch_import():
    """测试批量导入"""
    print("=" * 50)
    print("测试工具批量导入功能")
    print("=" * 50)
    
    # 执行批量导入
    print("\n1. 发送批量导入请求...")
    response = requests.post(
        f"{BASE_URL}/api/tools/batch-import",
        json=test_tools,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n导入结果:")
        print(f"  成功: {result['created']}")
        print(f"  跳过: {result['skipped']}")
        print(f"  失败: {result['errors']}")
        
        if result['created_tools']:
            print("\n创建的工具:")
            for tool in result['created_tools']:
                print(f"  - {tool['name']} (ID: {tool['id']})")
        
        if result['skipped_tools']:
            print("\n跳过的工具:")
            for tool in result['skipped_tools']:
                print(f"  - {tool['name']}: {tool['reason']}")
        
        if result['error_details']:
            print("\n错误详情:")
            for error in result['error_details']:
                print(f"  - {error['name']}: {error['error']}")
    else:
        print(f"错误: {response.text}")
    
    # 验证工具是否创建成功
    print("\n2. 验证工具列表...")
    response = requests.get(f"{BASE_URL}/api/tools/")
    if response.status_code == 200:
        tools = response.json()
        print(f"当前工具总数: {len(tools)}")
        test_tools_found = [t for t in tools if t['name'].startswith('test_tool_')]
        print(f"测试工具数量: {len(test_tools_found)}")
    
    print("\n" + "=" * 50)


def cleanup_test_tools():
    """清理测试工具"""
    print("\n清理测试工具...")
    response = requests.get(f"{BASE_URL}/api/tools/")
    if response.status_code == 200:
        tools = response.json()
        for tool in tools:
            if tool['name'].startswith('test_tool_'):
                delete_response = requests.delete(f"{BASE_URL}/api/tools/{tool['id']}")
                if delete_response.status_code == 204:
                    print(f"  已删除: {tool['name']}")
                else:
                    print(f"  删除失败: {tool['name']}")


if __name__ == "__main__":
    try:
        # 先清理可能存在的测试数据
        cleanup_test_tools()
        
        # 执行测试
        test_batch_import()
        
        # 再次执行测试（测试重复导入的情况）
        print("\n\n测试重复导入...")
        test_batch_import()
        
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器，请确保后端服务已启动")
    except Exception as e:
        print(f"错误: {e}")
    finally:
        # 清理测试数据
        print("\n")
        cleanup_test_tools()

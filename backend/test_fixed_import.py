# -*- coding: utf-8 -*-
"""测试修复后的工具导入功能"""
import sys
sys.path.append('.')

from app.models.tool_definition import ToolDefinitionCreate

# 测试用例1：空的 parameters
test_empty_params = {
    "name": "test_empty_params",
    "description": "测试空参数",
    "parameters": {}
}

# 测试用例2：包含 results 字段
test_with_results = {
    "name": "test_with_results",
    "description": "测试包含results字段",
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
    "results": {  # 这个应该被忽略
        "type": "object",
        "properties": {
            "result1": {
                "type": "string"
            }
        }
    }
}

# 测试用例3：None parameters
test_none_params = {
    "name": "test_none_params",
    "description": "测试None参数"
}

print("=" * 70)
print("测试工具定义修复")
print("=" * 70)

# 测试1
print("\n测试 1: 空的 parameters: {}")
try:
    tool1 = ToolDefinitionCreate(**test_empty_params)
    print(f"✅ 成功创建工具: {tool1.name}")
    print(f"   parameters: {tool1.parameters}")
except Exception as e:
    print(f"❌ 失败: {e}")

# 测试2
print("\n测试 2: 包含 results 字段（应该被忽略）")
try:
    tool2 = ToolDefinitionCreate(**test_with_results)
    print(f"✅ 成功创建工具: {tool2.name}")
    tool_dict = tool2.model_dump()
    if "results" in tool_dict:
        print(f"   ❌ results 字段未被忽略")
    else:
        print(f"   ✅ results 字段已被忽略")
except Exception as e:
    print(f"❌ 失败: {e}")

# 测试3
print("\n测试 3: 没有 parameters 字段")
try:
    tool3 = ToolDefinitionCreate(**test_none_params)
    print(f"✅ 成功创建工具: {tool3.name}")
    print(f"   parameters: {tool3.parameters}")
except Exception as e:
    print(f"❌ 失败: {e}")

print("\n" + "=" * 70)
print("测试完成！")
print("=" * 70)

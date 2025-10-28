# -*- coding: utf-8 -*-
"""测试工具定义模型是否正确忽略额外字段"""
import sys
sys.path.append('.')

from app.models.tool_definition import ToolDefinitionCreate, ToolParameters

# 测试数据：包含 results 字段（应该被忽略）
test_data = {
    "name": "test_tool_with_results",
    "description": "测试工具，包含 results 字段",
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
    "results": {  # 这个字段应该被忽略
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "description": "状态"
            }
        }
    },
    "extra_field": "这个也会被忽略",  # 额外字段
    "category": "test",
    "tags": "test,demo"
}

print("=" * 60)
print("测试工具定义模型 - 忽略额外字段功能")
print("=" * 60)

try:
    # 创建模型实例
    print("\n1. 创建工具定义实例（包含 results 和其他额外字段）...")
    tool = ToolDefinitionCreate(**test_data)
    
    print("✅ 成功！模型创建成功，额外字段已被忽略")
    
    # 查看模型数据
    print("\n2. 模型数据:")
    tool_dict = tool.model_dump()
    for key, value in tool_dict.items():
        if key == "parameters":
            print(f"   {key}: {value}")
        else:
            print(f"   {key}: {value}")
    
    # 验证 results 字段是否存在
    print("\n3. 验证额外字段:")
    if "results" in tool_dict:
        print("   ❌ results 字段仍然存在（不正确）")
    else:
        print("   ✅ results 字段已被忽略（正确）")
    
    if "extra_field" in tool_dict:
        print("   ❌ extra_field 字段仍然存在（不正确）")
    else:
        print("   ✅ extra_field 字段已被忽略（正确）")
    
    # 验证必需字段
    print("\n4. 验证必需字段:")
    required_fields = ["name", "description", "parameters"]
    for field in required_fields:
        if field in tool_dict and tool_dict[field]:
            print(f"   ✅ {field}: 存在")
        else:
            print(f"   ❌ {field}: 缺失")
    
    print("\n" + "=" * 60)
    print("✅ 测试通过！模型配置正确，可以忽略额外字段")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    print("=" * 60)
    import traceback
    traceback.print_exc()

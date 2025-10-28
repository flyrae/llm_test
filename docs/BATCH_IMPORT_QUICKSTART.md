# 工具批量导入功能使用指南

## 快速开始

### 1. 准备工具定义JSON文件

创建一个JSON文件（例如 `my_tools.json`），包含要导入的工具定义：

```json
[
  {
    "name": "get_weather",
    "description": "获取天气信息",
    "category": "web",
    "parameters": {
      "type": "object",
      "properties": {
        "location": {
          "type": "string",
          "description": "城市名称"
        }
      },
      "required": ["location"]
    },
    "tags": "weather,api"
  }
]
```

### 2. 通过界面导入

1. 打开浏览器，访问工具管理页面
2. 点击右上角的 **"批量导入"** 按钮
3. 将JSON内容粘贴到文本框中
4. 点击 **"开始导入"** 按钮
5. 查看导入结果

### 3. 或者通过API导入

```bash
curl -X POST http://localhost:8000/api/tools/batch-import \
  -H "Content-Type: application/json" \
  -d @my_tools.json
```

## 功能特性

✅ **批量创建**: 一次导入多个工具定义  
✅ **重复检测**: 自动跳过已存在的工具名称  
✅ **错误处理**: 详细的错误信息反馈  
✅ **事务支持**: 确保数据一致性  
✅ **结果统计**: 显示成功、跳过和失败的数量  

## 测试

运行测试脚本验证功能：

```bash
cd backend
python test_batch_import.py
```

## 示例文件

- `docs/batch_import_example.json` - 包含5个示例工具的完整JSON文件
- 可以直接复制使用或作为模板修改

## 常见问题

**Q: 如果工具名称重复会怎样？**  
A: 系统会自动跳过该工具，不会覆盖现有数据，并在结果中显示跳过原因。

**Q: 支持哪些字段？**  
A: 必填字段: `name`, `description`；可选字段: `category`, `parameters`, `example_call`, `tags`

**Q: JSON格式错误怎么办？**  
A: 系统会提示JSON格式错误，请检查JSON语法是否正确。

**Q: 可以导入多少个工具？**  
A: 理论上没有限制，但建议每次导入不超过100个以保证性能。

## 详细文档

查看完整文档：`BATCH_IMPORT_TOOLS.md`

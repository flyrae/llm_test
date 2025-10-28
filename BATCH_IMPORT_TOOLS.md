# 工具管理批量导入功能

## 功能说明

工具管理页面新增了批量导入功能，允许用户通过JSON格式一次性导入多个工具定义。

## 使用方法

1. **打开批量导入弹窗**
   - 在工具管理页面点击右上角的"批量导入"按钮
   - 系统会显示批量导入对话框

2. **准备JSON数据**
   - 按照指定格式准备工具定义的JSON数组
   - 可以参考 `docs/batch_import_example.json` 中的示例

3. **执行导入**
   - 将准备好的JSON数据粘贴到文本框中
   - 点击"开始导入"按钮
   - 系统会逐个处理并显示导入结果

## JSON格式说明

JSON数据必须是一个数组，每个元素包含以下字段：

```json
[
  {
    "name": "工具名称",              // 必填，字符串，唯一标识
    "description": "工具描述",       // 必填，字符串
    "category": "分类",              // 可选，字符串
    "parameters": {                  // 可选，JSON Schema格式
      "type": "object",
      "properties": {
        "参数名": {
          "type": "参数类型",
          "description": "参数描述"
        }
      },
      "required": ["必需参数列表"]
    },
    "example_call": {                // 可选，示例调用
      "参数名": "参数值"
    },
    "tags": "标签1,标签2"            // 可选，逗号分隔的标签
  }
]
```

### 字段说明

- **name** (必填): 工具的唯一名称，如果已存在同名工具，将跳过导入
- **description** (必填): 工具的功能描述
- **category** (可选): 工具分类，如 web、file、math 等
- **parameters** (可选): 工具参数定义，使用JSON Schema格式
  - `type`: 通常为 "object"
  - `properties`: 参数定义对象
  - `required`: 必需参数名称数组
- **example_call** (可选): 工具调用示例
- **tags** (可选): 标签字符串，多个标签用逗号分隔

## 导入结果

导入完成后，系统会显示详细的导入结果：

- **成功导入**: 显示成功创建的工具数量和名称列表
- **跳过**: 显示因名称重复而跳过的工具及原因
- **失败**: 显示导入失败的工具及错误信息

## 示例

参考 `docs/batch_import_example.json` 文件，其中包含5个示例工具：

1. **get_weather**: 获取天气信息的Web API工具
2. **calculate_sum**: 数学计算工具
3. **read_file**: 文件读取工具
4. **send_email**: 邮件发送工具
5. **search_database**: 数据库搜索工具

## 注意事项

1. JSON格式必须正确，否则会提示格式错误
2. 如果工具名称已存在，该工具会被跳过，不会覆盖现有工具
3. 建议先在小范围测试导入功能，确认无误后再批量导入
4. 导入前可以先导出现有工具作为备份

## API端点

后端API端点: `POST /api/tools/batch-import`

请求体: JSON数组，包含多个工具定义对象

响应体:
```json
{
  "created": 5,
  "skipped": 2,
  "errors": 0,
  "created_tools": [
    {"id": 1, "name": "tool1"},
    ...
  ],
  "skipped_tools": [
    {"name": "tool2", "reason": "工具名称已存在"}
  ],
  "error_details": []
}
```

## 技术实现

### 后端 (backend/app/api/tools.py)
- 新增 `POST /api/tools/batch-import` 端点
- 支持事务处理，确保数据一致性
- 提供详细的导入结果反馈

### 前端 (frontend/pages/tools.html)
- 添加"批量导入"按钮
- 实现导入弹窗UI
- JSON格式验证
- 显示详细的导入结果（成功、跳过、失败）

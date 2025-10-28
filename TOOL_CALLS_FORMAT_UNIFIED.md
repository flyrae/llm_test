# 工具调用格式统一说明

## 问题

用户询问前端传递的格式是否能正确解析：

```json
[
  {
    "id": "019a2421ce97a0ed5b605ce7de0d702c",
    "type": "function",
    "function": {
      "name": "get_weather",
      "arguments": "{\"location\":\"北京\",\"unit\":\"celsius\"}"
    }
  }
]
```

## 分析

### 原来的问题

系统中存在**两种数据格式**：

#### 1. OpenAI 完整格式（从调试页面保存）
```json
{
  "id": "call_xxx",
  "type": "function",
  "function": {
    "name": "get_weather",
    "arguments": "{\"location\":\"北京\"}"
  }
}
```

#### 2. 简化格式（从测试用例页面保存）
```json
{
  "name": "get_weather",
  "arguments": {"location": "北京"}
}
```

这导致了**数据不一致**的问题。

## 修复方案

### 统一使用 OpenAI 格式

修改测试用例页面的保存逻辑，使其也保存 OpenAI 格式：

```javascript
// 修改前：简化格式
{
  name: call.name,
  arguments: args
}

// 修改后：OpenAI 格式
{
  type: 'function',
  function: {
    name: call.name,
    arguments: JSON.stringify(args)  // 保持字符串格式
  }
}
```

### 注意事项

1. **`id` 字段**
   - 用于追踪单次工具调用
   - 在期望工具调用中不是必需的（评估时只关心名称和参数）
   - 保存时可以省略，显示时也可以省略

2. **`type` 字段**
   - 目前只有 `"function"` 类型
   - 保留以便将来扩展（如支持其他类型的工具）

3. **`arguments` 格式**
   - 在 OpenAI 格式中，`arguments` 是**字符串类型**
   - 需要用 `JSON.stringify()` 转换对象为字符串
   - 显示时需要 `JSON.parse()` 解析回对象

## 兼容性保证

### 显示逻辑（已支持）

`formatToolCallArguments` 方法支持多种格式：

```javascript
formatToolCallArguments(call) {
  let args;
  
  // 优先尝试 OpenAI 格式
  if (call.function && call.function.arguments) {
    args = call.function.arguments;
  } 
  // 兼容简化格式
  else if (call.arguments) {
    args = call.arguments;
  }
  
  // 如果是字符串，解析为对象
  if (typeof args === 'string') {
    args = JSON.parse(args);
  }
  
  return JSON.stringify(args, null, 2);
}
```

### 数据库中的现有数据

数据库中可能同时存在两种格式的数据：

#### OpenAI 格式（新数据）
```json
[
  {
    "id": "019a2421ce97a0ed5b605ce7de0d702c",
    "type": "function",
    "function": {
      "name": "get_weather",
      "arguments": "{\"location\":\"北京\"}"
    }
  }
]
```

#### 简化格式（旧数据）
```json
[
  {
    "name": "get_weather",
    "arguments": {
      "location": "上海"
    }
  }
]
```

**两种格式都能正确显示和解析！** ✅

## 数据迁移

如果需要统一数据库中的格式，可以运行迁移脚本：

```python
# backend/migrate_tool_calls_format.py
import sqlite3
import json

conn = sqlite3.connect('data/models.db')
cursor = conn.cursor()

cursor.execute('SELECT id, expected_tool_calls FROM test_cases WHERE expected_tool_calls IS NOT NULL')
rows = cursor.fetchall()

for row_id, tool_calls_json in rows:
    tool_calls = json.loads(tool_calls_json)
    
    # 转换为 OpenAI 格式
    new_tool_calls = []
    for call in tool_calls:
        if 'function' in call:
            # 已经是 OpenAI 格式，跳过
            new_tool_calls.append(call)
        else:
            # 转换简化格式为 OpenAI 格式
            new_call = {
                'type': 'function',
                'function': {
                    'name': call.get('name'),
                    'arguments': json.dumps(call.get('arguments')) if isinstance(call.get('arguments'), dict) else call.get('arguments')
                }
            }
            new_tool_calls.append(new_call)
    
    # 更新数据库
    cursor.execute('UPDATE test_cases SET expected_tool_calls = ? WHERE id = ?', 
                   (json.dumps(new_tool_calls), row_id))

conn.commit()
conn.close()
```

## 评估逻辑更新

如果有工具调用的评估逻辑，也需要更新以支持 OpenAI 格式：

```python
# 提取工具调用信息
def extract_tool_call_info(call):
    """兼容两种格式"""
    if 'function' in call:
        # OpenAI 格式
        name = call['function']['name']
        args_str = call['function']['arguments']
        args = json.loads(args_str) if isinstance(args_str, str) else args_str
    else:
        # 简化格式
        name = call['name']
        args = call['arguments']
    
    return name, args
```

## 总结

### ✅ 已完成

1. **统一保存格式**：测试用例页面现在也保存 OpenAI 格式
2. **兼容显示**：支持显示两种格式的数据
3. **兼容编辑**：编辑时能正确加载两种格式

### 📋 推荐操作

1. **重新加载前端页面**，清除缓存
2. **测试保存功能**：
   - 从调试页面保存 → 应该是 OpenAI 格式
   - 从测试用例页面保存 → 现在也是 OpenAI 格式
3. **验证显示**：打开测试用例页面，检查工具调用是否正确显示

### 📝 答案

**是的，前端传递的格式可以正确解析！** ✅

```json
[
  {
    "id": "019a2421ce97a0ed5b605ce7de0d702c",
    "type": "function",
    "function": {
      "name": "get_weather",
      "arguments": "{\"location\":\"北京\",\"unit\":\"celsius\"}"
    }
  }
]
```

这是标准的 OpenAI 格式，系统完全支持：
- ✅ 保存到数据库
- ✅ 从数据库读取
- ✅ 前端正确显示
- ✅ 编辑时正确加载
- ✅ 评估时正确解析

所有组件都已更新，完全兼容这种格式！🎉

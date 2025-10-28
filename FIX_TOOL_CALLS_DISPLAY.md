# 期望工具调用显示问题修复

## 问题描述

用户报告：期望的工具调用没有正确保存到测试用例中。

## 问题分析

经过检查发现：

1. ✅ **数据已正确保存到数据库**
   - 使用数据库检查脚本确认 `expected_tool_calls` 字段有数据
   - 数据格式正确（OpenAI格式）

2. ❌ **前端显示逻辑有问题**
   - 前端代码假设数据格式是简化格式：`{name, arguments}`
   - 实际保存的数据是 OpenAI 格式：`{function: {name, arguments}}`
   - 导致显示时无法正确读取数据

## 数据格式对比

### 实际保存的格式（OpenAI格式）
```json
[
  {
    "id": "019a241747be10479f0511f9885f5174",
    "type": "function",
    "function": {
      "name": "get_weather",
      "arguments": "{\"location\":\"伦敦\",\"unit\":\"celsius\"}"
    }
  }
]
```

### 前端期望的格式（简化格式）
```json
[
  {
    "name": "get_weather",
    "arguments": {
      "location": "伦敦",
      "unit": "celsius"
    }
  }
]
```

## 修复内容

### 1. 修改测试用例列表页面显示 (`frontend/pages/testcases.html`)

#### a) 改进期望工具调用的显示组件
- 支持两种数据格式（OpenAI格式和简化格式）
- 添加更详细的显示，包括参数内容
- 改进UI样式，更清晰地展示工具调用信息

```html
<!-- 修改前 -->
<span class="font-mono">{{ call.name }}</span>

<!-- 修改后 -->
<span class="font-mono">{{ call.function ? call.function.name : call.name }}</span>
<div class="text-xs font-mono">{{ formatToolCallArguments(call) }}</div>
```

#### b) 添加 `formatToolCallArguments` 方法
- 智能识别数据格式
- 自动解析字符串类型的 JSON
- 格式化为易读的 JSON 显示

```javascript
formatToolCallArguments(call) {
    // 支持两种格式
    let args;
    if (call.function && call.function.arguments) {
        // OpenAI格式
        args = call.function.arguments;
    } else if (call.arguments) {
        // 简化格式
        args = call.arguments;
    }
    
    // 如果是字符串，尝试解析
    if (typeof args === 'string') {
        args = JSON.parse(args);
    }
    
    return JSON.stringify(args, null, 2);
}
```

#### c) 修复编辑测试用例时的数据转换
- 在加载测试用例进行编辑时，正确识别并转换两种格式
- 确保编辑表单能正确显示现有数据

### 2. 创建数据库检查工具 (`backend/check_tool_calls.py`)

用于快速检查数据库中的工具调用数据：

```bash
cd backend
python check_tool_calls.py
```

## 测试验证

### 验证步骤

1. **打开测试用例页面**
   - 访问 `/pages/testcases.html`
   - 查看已有测试用例的"期望的工具调用"部分

2. **应该能看到**
   - 🔧 工具名称（如 `get_weather`）
   - 📋 格式化的参数JSON

3. **编辑测试用例**
   - 点击编辑按钮
   - 期望工具调用应该正确显示在表单中
   - 参数应该是格式化的JSON

4. **从调试页面保存**
   - 在调试页面测试工具调用
   - 保存为测试用例
   - 在测试用例页面查看，应该正确显示

## 兼容性说明

修复后的代码**完全兼容**两种数据格式：

### OpenAI 格式（推荐）
```json
{
  "function": {
    "name": "tool_name",
    "arguments": "{\"key\": \"value\"}"
  }
}
```

### 简化格式（也支持）
```json
{
  "name": "tool_name",
  "arguments": {"key": "value"}
}
```

## 已修复的文件

1. ✅ `backend/app/models/test_case.py` - 数据模型类型定义（支持 tool_calls）
2. ✅ `frontend/pages/testcases.html` - 测试用例列表页面显示
3. ✅ `frontend/pages/debug.html` - 调试页面工具调用保存（已在之前修复）
4. ✅ `backend/check_tool_calls.py` - 数据库检查工具

## 相关问题修复

这次修复同时解决了以下相关问题：

1. ✅ 422错误 - 对话历史类型验证问题
2. ✅ 工具调用保存 - 正确保存到数据库
3. ✅ 工具调用显示 - 在测试用例页面正确显示
4. ✅ 对话历史显示 - 在调试页面显示工具调用

## 数据库检查脚本使用

如果需要检查数据库中的工具调用数据：

```powershell
cd backend
D:\mambaforge\envs\modelscope\python.exe check_tool_calls.py
```

输出示例：
```
Found database: data/models.db
Tables: ['models', 'test_cases', 'test_results', 'tool_definitions']

Recent 5 test cases:
ID: 3
Title: 工具测试1
Expected Tool Calls: [
  {
    "function": {
      "name": "get_weather",
      "arguments": "{\"location\":\"伦敦\",\"unit\":\"celsius\"}"
    }
  }
]
```

## 总结

**问题根源**：前端显示逻辑与实际数据格式不匹配

**解决方案**：修改前端代码以支持 OpenAI 格式的工具调用数据

**结果**：
- ✅ 数据正确保存
- ✅ 前端正确显示
- ✅ 编辑功能正常
- ✅ 向后兼容

现在期望的工具调用应该能够正确地保存和显示了！🎉

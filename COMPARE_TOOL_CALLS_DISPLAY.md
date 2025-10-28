# 对比测试页面 - 添加工具调用显示

## 改进内容

在对比测试页面的"查看完整输出"模态框中，添加了工具调用结果的显示。

## 问题

之前的"完整输出"只显示文本内容：

```html
<pre>{{ currentOutput?.output }}</pre>
```

如果模型调用了工具但没有文本输出，或者用户想查看工具调用的详细信息，就无法看到。

## 解决方案

### 1. 改进的模态框结构

现在"完整输出"模态框分为三个部分：

#### a) 文本输出
```html
<div v-if="currentOutput?.output">
  <h3>文本输出</h3>
  <pre>{{ currentOutput.output }}</pre>
</div>
```

#### b) 工具调用
```html
<div v-if="currentOutput?.tool_calls && currentOutput.tool_calls.length > 0">
  <h3>工具调用</h3>
  <div v-for="call in currentOutput.tool_calls">
    <!-- 工具名称 -->
    <span>{{ call.function.name }}</span>
    <!-- 参数 -->
    <pre>{{ formatToolCallArguments(call) }}</pre>
  </div>
</div>
```

#### c) 无输出提示
```html
<div v-if="无文本且无工具调用">
  <i class="fas fa-inbox"></i>
  <p>无输出内容</p>
</div>
```

### 2. 工具调用显示样式

每个工具调用显示：
- 🔧 **工具名称**：黄色高亮显示
- 🆔 **调用ID**：右上角显示（如果有）
- 📋 **参数**：格式化的 JSON，白色背景显示

```
┌──────────────────────────────────────┐
│ get_weather          call_abc123     │
│ 参数:                                 │
│ {                                    │
│   "location": "北京",                │
│   "unit": "celsius"                  │
│ }                                    │
└──────────────────────────────────────┘
```

### 3. 添加格式化方法

添加 `formatToolCallArguments` 方法，支持两种工具调用格式：

```javascript
formatToolCallArguments(call) {
    let args;
    
    // 支持 OpenAI 格式
    if (call.function && call.function.arguments) {
        args = call.function.arguments;
    }
    // 支持简化格式
    else if (call.arguments) {
        args = call.arguments;
    }
    
    // 如果是字符串，解析为对象
    if (typeof args === 'string') {
        args = JSON.parse(args);
    }
    
    // 格式化为易读的 JSON
    return JSON.stringify(args, null, 2);
}
```

## 使用场景

### 场景 1：只有文本输出

**对话：** "你好"

**显示：**
```
📝 文本输出
你好！有什么可以帮助你的吗？
```

### 场景 2：只有工具调用

**对话：** "北京今天天气怎么样"

**显示：**
```
🔧 工具调用

get_weather
参数:
{
  "location": "北京",
  "unit": "celsius"
}
```

### 场景 3：文本 + 工具调用

**对话：** "帮我查一下北京天气"

**显示：**
```
📝 文本输出
好的，让我帮您查询北京的天气信息。

🔧 工具调用

get_weather
参数:
{
  "location": "北京",
  "unit": "celsius"
}
```

### 场景 4：多个工具调用

**对话：** "比较北京和上海的天气"

**显示：**
```
📝 文本输出
让我为您查询这两个城市的天气。

🔧 工具调用

get_weather
参数:
{
  "location": "北京",
  "unit": "celsius"
}

get_weather
参数:
{
  "location": "上海",
  "unit": "celsius"
}
```

### 场景 5：无输出

**显示：**
```
📦
无输出内容
```

## 视觉效果

### 颜色方案

- **文本输出**：灰色背景 (`bg-gray-50`)，灰色文字
- **工具调用**：黄色背景 (`bg-yellow-50`)，黄色边框
- **参数**：白色背景，等宽字体

### 图标使用

- 📝 `fa-comment-dots` - 文本输出
- 🔧 `fa-wrench` - 工具调用
- 📦 `fa-inbox` - 无输出

## 数据格式支持

### OpenAI 格式
```json
{
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "get_weather",
        "arguments": "{\"location\":\"北京\"}"
      }
    }
  ]
}
```

### 简化格式
```json
{
  "tool_calls": [
    {
      "name": "get_weather",
      "arguments": {
        "location": "北京"
      }
    }
  ]
}
```

两种格式都能正确显示！

## 优势

### 1. 信息完整
- ✅ 文本输出和工具调用都能看到
- ✅ 不会遗漏任何输出信息

### 2. 结构清晰
- ✅ 分区显示，一目了然
- ✅ 黄色高亮，工具调用易识别

### 3. 详细信息
- ✅ 显示工具名称
- ✅ 显示调用 ID
- ✅ 格式化的参数 JSON

### 4. 用户体验
- ✅ 易于阅读和理解
- ✅ 专业的视觉效果
- ✅ 响应式设计

## 测试建议

1. **测试纯文本输出**
   - 运行一个不涉及工具的测试用例
   - 查看完整输出
   - 应该只显示文本部分

2. **测试工具调用**
   - 运行一个涉及 Function Calling 的测试用例
   - 查看完整输出
   - 应该显示工具调用部分

3. **测试混合输出**
   - 运行一个既有文本又有工具调用的测试
   - 查看完整输出
   - 两部分都应该正确显示

4. **测试多工具调用**
   - 运行一个调用多个工具的测试
   - 查看完整输出
   - 所有工具调用都应该列出

5. **测试无输出**
   - 运行一个失败或无输出的测试
   - 查看完整输出
   - 应该显示"无输出内容"提示

## 相关文件

- 修改文件：`frontend/pages/compare.html`
- 添加方法：`formatToolCallArguments`
- 改进组件：完整输出模态框

## 兼容性

- ✅ 向后兼容：旧的测试结果（只有文本）仍然正常显示
- ✅ 新功能：新的测试结果（包含工具调用）完整显示
- ✅ 灵活格式：支持 OpenAI 和简化两种格式

现在对比测试页面的"查看完整输出"功能更加完善了！🎉

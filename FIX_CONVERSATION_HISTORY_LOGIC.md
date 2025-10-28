# 修复对话历史保存逻辑 - 排除当前轮

## 问题描述

用户反馈：最后一轮的对话数据不应该被保存为历史记录。

## 问题分析

### 错误的逻辑

之前的逻辑是这样的：

```javascript
// 对话过程中：conversationHistory 包含所有轮次
conversationHistory = [
  {role: 'user', content: '今天天气怎么样'},     // 第1轮 - 用户
  {role: 'assistant', content: '...'},          // 第1轮 - 助手
  {role: 'user', content: '北京'},              // 第2轮 - 用户（当前轮）
  {role: 'assistant', content: '...'}           // 第2轮 - 助手（当前轮）
]

// 保存时：
conversation_history: conversationHistory  // 包含了当前轮！❌
prompt: lastRequest.prompt  // "北京"
```

**问题**：当前轮的数据被重复保存了
- `prompt` 保存了当前轮的用户输入
- `conversation_history` 中也包含了当前轮
- 期望输出对应的也是当前轮的助手回复

### 正确的逻辑

```javascript
// 保存时：
conversation_history: conversationHistory.slice(0, -2)  // 去掉当前轮
prompt: "北京"  // 当前轮的用户输入
expected_output: "..."  // 当前轮的期望输出
```

## 修复方案

### 核心逻辑

```javascript
// 处理对话历史
let conversationHistoryToSave = null;

if (this.conversationHistory.length > 2) {
    // 多轮对话：去掉最后两条（当前轮的用户输入和助手回复）
    conversationHistoryToSave = this.conversationHistory.slice(0, -2);
}
// 如果只有2条或更少，说明是单轮对话，不保存历史

const testCaseData = {
    conversation_history: conversationHistoryToSave,
    prompt: this.lastRequest.prompt,  // 当前轮的用户输入
    expected_output: this.testCaseForm.expected_output,  // 当前轮的期望输出
    ...
};
```

### 为什么用 `slice(0, -2)`？

- `-2` 表示从倒数第2个元素开始（不包括）
- `slice(0, -2)` 会返回从开头到倒数第2个之前的所有元素
- 正好去掉最后两条消息（当前轮的用户输入和助手回复）

## 场景说明

### 场景 1：单轮对话

**对话过程：**
```
用户: "今天天气怎么样"
助手: "今天天气晴朗..."
```

**conversationHistory 内容：**
```javascript
[
  {role: 'user', content: '今天天气怎么样'},
  {role: 'assistant', content: '今天天气晴朗...'}
]
// length = 2
```

**保存为测试用例：**
```json
{
  "conversation_history": null,
  "prompt": "今天天气怎么样",
  "expected_output": "今天天气晴朗..."
}
```

---

### 场景 2：两轮对话

**对话过程：**
```
第1轮：
  用户: "今天天气怎么样"
  助手: "今天天气晴朗..."

第2轮（当前）：
  用户: "北京"
  助手: "北京今天晴，20-25度..."
```

**conversationHistory 内容：**
```javascript
[
  {role: 'user', content: '今天天气怎么样'},      // 第1轮
  {role: 'assistant', content: '今天天气晴朗...'}, // 第1轮
  {role: 'user', content: '北京'},                // 第2轮（当前）
  {role: 'assistant', content: '北京今天晴...'}   // 第2轮（当前）
]
// length = 4
```

**保存为测试用例：**
```json
{
  "conversation_history": [
    {"role": "user", "content": "今天天气怎么样"},
    {"role": "assistant", "content": "今天天气晴朗..."}
  ],
  "prompt": "北京",
  "expected_output": "北京今天晴，20-25度..."
}
```

**说明：**
- `conversation_history` 只包含第1轮（作为上下文）
- `prompt` 是第2轮的用户输入
- `expected_output` 是第2轮的期望输出

---

### 场景 3：三轮对话

**对话过程：**
```
第1轮：
  用户: "今天天气怎么样"
  助手: "今天天气晴朗..."

第2轮：
  用户: "北京"
  助手: "北京今天晴..."

第3轮（当前）：
  用户: "那明天呢"
  助手: "明天预计多云..."
```

**conversationHistory 内容：**
```javascript
[
  {role: 'user', content: '今天天气怎么样'},      // 第1轮
  {role: 'assistant', content: '今天天气晴朗...'}, // 第1轮
  {role: 'user', content: '北京'},                // 第2轮
  {role: 'assistant', content: '北京今天晴...'},   // 第2轮
  {role: 'user', content: '那明天呢'},            // 第3轮（当前）
  {role: 'assistant', content: '明天预计多云...'} // 第3轮（当前）
]
// length = 6
```

**保存为测试用例：**
```json
{
  "conversation_history": [
    {"role": "user", "content": "今天天气怎么样"},
    {"role": "assistant", "content": "今天天气晴朗..."},
    {"role": "user", "content": "北京"},
    {"role": "assistant", "content": "北京今天晴..."}
  ],
  "prompt": "那明天呢",
  "expected_output": "明天预计多云..."
}
```

**说明：**
- `conversation_history` 包含第1轮和第2轮（作为上下文）
- `prompt` 是第3轮的用户输入
- `expected_output` 是第3轮的期望输出

## UI 改进

### 预览信息显示

**单轮对话：**
```
对话类型：单轮对话
当前提示词：今天天气怎么样？...
```

**两轮对话：**
```
历史对话上下文：2 条消息（不包括当前轮）
当前提示词：北京...
```

**三轮对话：**
```
历史对话上下文：4 条消息（不包括当前轮）
当前提示词：那明天呢...
```

明确告知用户有多少条历史消息会被保存。

## 数据结构说明

### 测试用例的完整结构

```json
{
  "title": "测试多轮天气查询",
  "system_prompt": "你是一个天气助手",
  
  // 历史对话（不包括当前轮）
  "conversation_history": [
    {"role": "user", "content": "今天天气怎么样"},
    {"role": "assistant", "content": "今天天气晴朗..."}
  ],
  
  // 当前轮的用户输入
  "prompt": "北京",
  
  // 当前轮的期望输出
  "expected_output": "北京今天晴，20-25度...",
  
  // 当前轮的期望工具调用
  "expected_tool_calls": [...],
  
  "tools": [1],
  "meta_data": {...}
}
```

## 运行测试时的行为

当运行这个测试用例时：

1. **准备阶段**：
   - 加载 `system_prompt`
   - 加载 `conversation_history` 作为上下文

2. **执行阶段**：
   - 发送 `prompt` 给模型
   - 模型基于历史对话上下文生成回复

3. **评估阶段**：
   - 比较实际输出与 `expected_output`
   - 比较实际工具调用与 `expected_tool_calls`

## 优势

### 1. 数据结构清晰
- `conversation_history`：历史上下文
- `prompt`：当前输入
- `expected_output`：期望输出
- 三者职责明确，不重复

### 2. 测试更准确
- 测试的是：给定历史上下文 + 当前输入 → 期望输出
- 不会出现"自己评估自己"的情况

### 3. 复用性更好
- 可以基于同样的历史上下文，测试不同的 prompt
- 可以修改期望输出而不影响上下文

## 总结

### 核心改变

```javascript
// 修改前：包含当前轮
conversation_history: this.conversationHistory

// 修改后：排除当前轮
conversation_history: this.conversationHistory.slice(0, -2)
```

### 效果

- ✅ 单轮对话：不保存历史
- ✅ 多轮对话：只保存**之前的轮次**作为上下文
- ✅ 当前轮：作为 `prompt` 和期望输出保存
- ✅ 数据结构清晰，不重复

现在对话历史的保存逻辑完全正确了！🎉

# 修复单轮对话保存为历史记录的问题

## 问题描述

用户报告：保存为测试用例时，即使只有一轮对话，也被保存为对话历史记录了。

## 问题分析

### 原来的逻辑

```javascript
conversation_history: this.conversationHistory.length > 0 ? this.conversationHistory : null
```

问题：
- 只要有一轮对话，`conversationHistory` 就会有2条记录（用户消息 + 助手回复）
- `length > 0` 条件永远为真
- 导致单轮对话也被保存为"对话历史"

### 应该的行为

- **单轮对话**：只保存 `prompt`（用户输入），不保存 `conversation_history`
- **多轮对话**：保存完整的 `conversation_history`（所有历史消息）

## 修复方案

### 判断标准

```javascript
// 如果对话历史只有2条（一问一答），则不算多轮对话
const isMultiRound = this.conversationHistory.length > 2;
```

**为什么是 > 2？**
- 单轮对话：user → assistant（2条消息）
- 多轮对话：user → assistant → user → assistant（4条消息或更多）

### 修改后的逻辑

```javascript
// 判断是否为多轮对话
const isMultiRound = this.conversationHistory.length > 2;

const testCaseData = {
  ...
  conversation_history: isMultiRound ? this.conversationHistory : null,
  prompt: this.lastRequest.prompt,
  ...
};
```

## 数据结构对比

### 单轮对话（不保存历史）

```json
{
  "title": "测试单轮对话",
  "prompt": "今天天气怎么样？",
  "conversation_history": null,
  "expected_output": "今天天气晴朗..."
}
```

### 多轮对话（保存历史）

```json
{
  "title": "测试多轮对话",
  "prompt": "那明天呢？",
  "conversation_history": [
    {"role": "user", "content": "今天天气怎么样？"},
    {"role": "assistant", "content": "今天天气晴朗..."},
    {"role": "user", "content": "那明天呢？"},
    {"role": "assistant", "content": "明天预计..."}
  ],
  "expected_output": "明天预计..."
}
```

## UI 改进

### 预览信息更新

在保存测试用例的模态框中，现在会明确显示：

#### 单轮对话
```
对话类型：单轮对话（不保存历史记录）
当前提示词：今天天气怎么样？...
```

#### 多轮对话
```
多轮对话历史：4 条消息
当前提示词：那明天呢？...
```

这样用户可以清楚地知道是否会保存对话历史。

## 测试场景

### 场景 1：单轮对话
1. 打开调试页面
2. 输入："今天天气怎么样？"
3. 模型回复
4. 点击"保存为测试用例"
5. **预期**：显示"单轮对话（不保存历史记录）"
6. 保存后，`conversation_history` 字段应为 `null`

### 场景 2：两轮对话
1. 打开调试页面
2. 第一轮："今天天气怎么样？" → 模型回复
3. 第二轮："那明天呢？" → 模型回复
4. 点击"保存为测试用例"
5. **预期**：显示"多轮对话历史：4 条消息"
6. 保存后，`conversation_history` 包含完整的4条消息

### 场景 3：三轮对话
1. 继续上面的对话
2. 第三轮："后天呢？" → 模型回复
3. 点击"保存为测试用例"
4. **预期**：显示"多轮对话历史：6 条消息"
5. 保存后，`conversation_history` 包含完整的6条消息

## 数据库查询验证

使用检查脚本验证：

```bash
cd backend
python -c "import sqlite3, json; conn = sqlite3.connect('data/models.db'); cursor = conn.cursor(); cursor.execute('SELECT title, conversation_history FROM test_cases ORDER BY id DESC LIMIT 5'); [(print(f'{row[0]}: {\"多轮\" if row[1] else \"单轮\"}')) for row in cursor.fetchall()]; conn.close()"
```

## 优势

### 1. 数据更清晰
- 单轮测试用例结构简单，只有 `prompt` 和期望输出
- 多轮测试用例包含完整的上下文

### 2. 性能更好
- 单轮测试用例数据量更小
- 减少不必要的数据存储

### 3. 评估更准确
- 单轮测试：直接评估 prompt → output
- 多轮测试：评估整个对话流程，包括上下文理解

### 4. 用户体验更好
- 清楚地告知用户是否会保存对话历史
- 避免误解和混淆

## 兼容性

### 现有数据
- ✅ 不影响已保存的测试用例
- ✅ 读取时仍然支持两种格式

### 评估逻辑
如果评估代码需要区分：

```python
def is_multi_round(test_case):
    """判断是否为多轮对话测试"""
    return test_case.conversation_history is not None and len(test_case.conversation_history) > 2

def evaluate(test_case, model_output):
    if is_multi_round(test_case):
        # 多轮对话评估：考虑上下文
        context = test_case.conversation_history
        prompt = test_case.prompt
    else:
        # 单轮对话评估：直接评估
        prompt = test_case.prompt
        context = None
    
    # ... 评估逻辑
```

## 总结

### 修改内容
1. ✅ 修改保存逻辑：单轮对话不保存 `conversation_history`
2. ✅ 更新预览信息：明确显示对话类型
3. ✅ 添加判断标准：`length > 2` 区分单轮和多轮

### 效果
- ✅ 单轮对话：`conversation_history = null`
- ✅ 多轮对话：`conversation_history = [...]`（完整历史）
- ✅ 用户明确看到保存的内容

现在单轮对话不会被错误地保存为历史记录了！🎉

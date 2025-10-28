# 修复对比页面工具调用数据来源问题

## 问题

点击"查看完整输出"时，弹窗显示"无输出内容"，工具调用没有显示。

## 原因分析

### 1. 数据库结构

`test_results` 表的字段：
```sql
id (INTEGER)
test_case_id (INTEGER)
model_id (INTEGER)
output (TEXT)           -- 只存储文本输出
metrics (JSON)          -- 存储所有性能指标和评估结果
score (FLOAT)
status (VARCHAR(20))
error_message (TEXT)
```

**注意**：表中没有独立的 `tool_calls` 字段！

### 2. 数据存储位置

工具调用信息存储在 `metrics` JSON 字段中：

```json
{
  "response_time": 1.988,
  "prompt_tokens": 154,
  "completion_tokens": 27,
  "total_tokens": 181,
  "estimated_cost": 0.0,
  "evaluation": {
    "tool_calls": {
      "expected": [...],
      "actual": [              ← 实际的工具调用在这里！
        {
          "name": "get_weather",
          "arguments": {
            "location": "上海",
            "unit": "celsius"
          }
        }
      ],
      "name_match": 20.0,
      "count_match": 20.0,
      "params_match": 30.0,
      "values_match": 30.0
    },
    "weights_used": {...},
    "scores": {...},
    "total_score": 1.0
  }
}
```

### 3. 前端代码问题

之前的代码直接从 `modelResult` 对象中查找 `tool_calls`：

```javascript
showFullOutput(modelResult) {
    this.currentOutput = modelResult;  // 直接赋值
    this.showOutputModal = true;
}
```

但是 `modelResult` 对象的结构是：
```javascript
{
  result_id: 8,
  model_id: 1,
  model_name: "deepseek-ai/DeepSeek-V3",
  output: null,             // 没有文本输出
  metrics: {...},           // 工具调用在这里面
  score: 1.0,
  status: "success"
}
```

所以 `currentOutput.tool_calls` 是 `undefined`，导致判断失败。

## 解决方案

修改 `showFullOutput` 方法，从 `metrics.evaluation.tool_calls.actual` 中提取工具调用：

```javascript
showFullOutput(modelResult) {
    // 从 metrics 中提取工具调用信息
    let toolCalls = null;
    if (modelResult.metrics && 
        modelResult.metrics.evaluation && 
        modelResult.metrics.evaluation.tool_calls && 
        modelResult.metrics.evaluation.tool_calls.actual) {
        toolCalls = modelResult.metrics.evaluation.tool_calls.actual;
    }
    
    // 创建一个新对象，包含提取的工具调用
    this.currentOutput = {
        ...modelResult,
        tool_calls: toolCalls  // 将工具调用添加到对象中
    };
    this.showOutputModal = true;
}
```

### 数据流程

1. **后端执行测试**：
   ```python
   result = await LLMService.call_model(...)
   # result 包含 tool_calls
   
   score, eval_details = EvaluationService.evaluate_result(
       tool_calls=result.get("tool_calls"),
       ...
   )
   # eval_details 包含 {'tool_calls': {'actual': [...]}}
   
   metrics = result.get("metrics", {})
   metrics['evaluation'] = eval_details  # 工具调用存入这里
   
   db_result = TestResultDB(
       output=result.get("output", ""),
       metrics=metrics,  # 保存到数据库
       ...
   )
   ```

2. **前端查询结果**：
   ```javascript
   // API 返回
   {
     output: "...",
     metrics: {
       evaluation: {
         tool_calls: {
           actual: [...]  // 工具调用在这里
         }
       }
     }
   }
   ```

3. **前端提取数据**：
   ```javascript
   // 从 metrics 中提取
   toolCalls = modelResult.metrics.evaluation.tool_calls.actual
   
   // 添加到 currentOutput
   currentOutput = {
       ...modelResult,
       tool_calls: toolCalls
   }
   ```

4. **模板显示**：
   ```html
   <div v-if="currentOutput?.tool_calls && currentOutput.tool_calls.length > 0">
       <!-- 显示工具调用 -->
   </div>
   ```

## 测试验证

### 1. 无工具调用的测试用例
```
输入: "你好"
输出: "你好！有什么可以帮助你的吗？"
工具调用: 无

显示: ✅ 只显示文本输出
```

### 2. 有工具调用的测试用例
```
输入: "上海今天天气怎么样"
输出: null
工具调用: [{"name": "get_weather", "arguments": {...}}]

显示: ✅ 显示工具调用部分（黄色高亮）
```

### 3. 文本 + 工具调用
```
输入: "帮我查一下北京天气"
输出: "好的，让我帮您查询。"
工具调用: [{"name": "get_weather", "arguments": {...}}]

显示: ✅ 两部分都显示
```

## 优化建议

### 方案 A：后端直接返回 tool_calls（推荐）

修改 `batch.py` 中的 `compare_results` 函数：

```python
compare_results[result.test_case_id]["results"].append({
    "result_id": result.id,
    "model_id": result.model_id,
    "model_name": model.name if model else "Unknown",
    "output": result.output,
    "tool_calls": result.metrics.get("evaluation", {}).get("tool_calls", {}).get("actual"),  # 直接提取
    "metrics": result.metrics,
    "score": result.score,
    "status": result.status
})
```

优点：
- 前端代码更简洁
- API 接口更清晰
- 数据结构更直观

### 方案 B：数据库添加 tool_calls 字段

添加 `tool_calls` 列到 `test_results` 表：

```python
# 迁移脚本
cursor.execute('''
    ALTER TABLE test_results 
    ADD COLUMN tool_calls JSON
''')
```

保存时同时存储：
```python
db_result = TestResultDB(
    output=result.get("output", ""),
    tool_calls=result.get("tool_calls"),  # 单独存储
    metrics=metrics,
    ...
)
```

优点：
- 数据结构更清晰
- 查询更方便
- 不依赖 metrics 结构

缺点：
- 需要数据库迁移
- 存在数据冗余

## 相关文件

- 修改文件：`frontend/pages/compare.html`
- 修改方法：`showFullOutput()`
- 数据来源：`metrics.evaluation.tool_calls.actual`

## 总结

这个问题的根本原因是**前端代码假设了错误的数据结构**。工具调用信息并不是存储在顶级的 `tool_calls` 字段中，而是嵌套在 `metrics.evaluation.tool_calls.actual` 路径下。

通过在 `showFullOutput` 方法中正确提取数据，现在可以正常显示工具调用信息了！✅

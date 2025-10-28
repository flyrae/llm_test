# 修复保存测试用例 422 错误

## 问题原因

保存测试用例时出现 422 错误（Unprocessable Entity），原因是 Pydantic 模型的类型验证失败。

具体问题：
- `conversation_history` 的类型定义为 `List[Dict[str, str]]`
- 但实际发送的数据中，助手消息包含 `tool_calls` 字段（是列表类型，不是字符串）
- 类型不匹配导致验证失败

## 修复内容

已修改 `backend/app/models/test_case.py` 中的类型定义：

### 修改前
```python
conversation_history: Optional[List[Dict[str, str]]] = None
```

### 修改后
```python
conversation_history: Optional[List[Dict[str, Any]]] = None  # 多轮对话历史（支持tool_calls）
```

同时更新了以下类：
- ✅ `TestCaseCreate`
- ✅ `TestCaseUpdate`
- ✅ `TestCaseResponse`

## 需要执行的操作

### 重启后端服务

修改了数据模型后，需要重启后端服务才能生效。

#### 方法1：使用PowerShell脚本
```powershell
# 在项目根目录执行
.\restart_server.ps1
```

#### 方法2：手动重启
```powershell
# 1. 停止当前服务（Ctrl+C 或关闭终端）

# 2. 重新启动
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 方法3：如果使用 VS Code 终端
1. 找到运行后端的终端
2. 按 `Ctrl+C` 停止服务
3. 再次运行启动命令

## 验证修复

重启服务后，尝试以下操作：

1. 在调试页面选择模型和工具
2. 发送一个会触发工具调用的消息（例如："今天伦敦天气怎么样"）
3. 模型返回工具调用
4. 点击"保存为测试用例"
5. 填写标题
6. 点击"使用工具调用作为期望"按钮
7. 点击"确认保存"

如果成功保存，说明修复生效。

## 数据结构示例

### 正确的 conversation_history 格式

```json
[
  {
    "role": "user",
    "content": "今天伦敦天气怎么样"
  },
  {
    "role": "assistant",
    "content": "",
    "tool_calls": [
      {
        "id": "019a241747be10479f0511f9885f5174",
        "type": "function",
        "function": {
          "name": "get_weather",
          "arguments": "{\"location\":\"伦敦\",\"unit\":\"celsius\"}"
        }
      }
    ]
  }
]
```

注意：
- `tool_calls` 是一个列表（数组）
- `content` 可以是空字符串
- 使用 `Dict[str, Any]` 可以灵活支持各种字段类型

## 技术说明

### Pydantic 类型系统

- `Dict[str, str]` - 字典的所有值必须是字符串
- `Dict[str, Any]` - 字典的值可以是任何类型（字符串、数字、列表、字典等）

由于对话历史消息可能包含：
- `content`: 字符串
- `role`: 字符串
- `tool_calls`: 列表（可选）

因此必须使用 `Dict[str, Any]` 来支持所有这些字段类型。

## 兼容性

这个修改完全向后兼容：
- ✅ 旧的测试用例（只有 content 和 role）仍然有效
- ✅ 新的测试用例（包含 tool_calls）现在可以正常保存
- ✅ 不影响已有功能

## 相关文件

- 修改文件：`backend/app/models/test_case.py`
- 影响的API：`POST /api/testcases/`
- 前端页面：`frontend/pages/debug.html`

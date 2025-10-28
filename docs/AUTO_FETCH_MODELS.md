# 自动获取端点模型列表功能

## 🎯 功能概述

新增了从API端点自动获取可用模型列表的功能，特别适用于：
- 阿里云DashScope
- OpenAI兼容的API端点  
- 企业内部API服务
- 其他支持 `/v1/models` 端点的服务

## 🚀 使用方法

### 1. 在添加模型时使用

1. **点击"添加模型"**
2. **输入API端点**
   ```
   例如: https://dashscope.aliyuncs.com/compatible-mode/v1
   ```
3. **输入API密钥**（如果需要）
4. **点击"获取模型"按钮**
5. **选择要使用的模型**
   - 可以全选所有模型
   - 或者单独选择需要的模型
6. **点击"使用选中的X个模型"**
7. **批量创建模型配置**

### 2. 支持的端点格式

系统会自动识别并转换不同的端点格式：

| 输入端点 | 自动转换为 |
|----------|------------|
| `https://api.openai.com/v1/chat/completions` | `https://api.openai.com/v1/models` |
| `https://dashscope.aliyuncs.com/compatible-mode/v1` | `https://dashscope.aliyuncs.com/compatible-mode/v1/models` |
| `https://your-api.com/v1` | `https://your-api.com/v1/models` |

## 📋 具体示例

### 示例1: 阿里云DashScope

```
1. API端点: https://dashscope.aliyuncs.com/compatible-mode/v1
2. API密钥: sk-c3868d72ebe54f93bf203742c4e2fd46
3. 点击"获取模型"
4. 系统返回: qwen-turbo, qwen-plus, qwen-max 等
5. 选择需要的模型，批量创建
```

### 示例2: OpenAI

```
1. API端点: https://api.openai.com/v1
2. API密钥: sk-your-openai-key
3. 获取模型: gpt-4, gpt-3.5-turbo, text-davinci-003 等
4. 批量创建配置
```

### 示例3: 企业内部API

```
1. API端点: https://internal-ai.company.com/v1
2. API密钥: internal-api-key
3. 获取企业内部可用模型
4. 批量配置
```

## 🔧 技术实现

### 后端API
```http
POST /api/models/fetch-models
Content-Type: application/json

{
    "api_endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "api_key": "sk-c3868d72ebe54f93bf203742c4e2fd46",
    "provider": "custom"
}
```

### 响应格式
```json
{
    "success": true,
    "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1/models",
    "models": [
        {
            "id": "qwen-turbo",
            "name": "qwen-turbo",
            "display_name": "qwen-turbo",
            "description": "Model: qwen-turbo",
            "owned_by": "alibaba"
        }
    ],
    "total": 15
}
```

## 🎨 前端功能

### 智能界面
- **一键获取**: 点击按钮自动获取模型列表
- **实时状态**: 显示获取进度和结果
- **模型选择**: 支持全选和单选模型
- **批量应用**: 将选中的模型应用到批量输入框

### 用户体验
- 自动填充批量输入框
- 实时显示模型数量
- 错误处理和友好提示

## 💡 使用场景

### 1. 快速探索新API
当你获得一个新的API端点时，可以快速查看它提供哪些模型。

### 2. 企业环境模型发现  
企业内部API可能经常更新模型，使用此功能可以自动发现新模型。

### 3. 减少手动输入错误
避免手动输入模型名称时的拼写错误。

### 4. 批量配置效率
从几十个可用模型中快速选择需要的进行批量配置。

## ⚠️ 注意事项

1. **API密钥权限**: 确保API密钥有查看模型列表的权限
2. **网络连接**: 需要能够访问目标API端点
3. **端点格式**: 目标API需要支持 `/v1/models` 或类似端点
4. **认证方式**: 支持Bearer Token和x-api-key两种认证方式

## 🔮 未来扩展

1. **模型详情获取**: 获取模型的详细信息（参数、能力等）
2. **定期同步**: 定期检查端点的模型更新
3. **模型分类**: 根据模型类型自动分类
4. **性能测试**: 获取模型列表后自动进行简单的性能测试

这个功能让模型配置变得更加智能和自动化，特别适合需要管理大量模型的企业环境！
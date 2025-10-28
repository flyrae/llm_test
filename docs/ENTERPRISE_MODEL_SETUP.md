# 企业内部模型部署配置指南

## 🏢 企业内部模型批量配置

对于公司内部部署的模型，现在支持两种灵活的批量添加方式：

### 方法1: 改进的添加模型功能（推荐）

#### 🎯 适用场景
- 企业内部统一端点，多个模型
- 自建模型服务
- 需要灵活配置的场景

#### 📝 使用步骤

1. **点击"添加模型"按钮**

2. **配置基本信息**
   ```
   模型名称前缀: 公司内部模型
   提供商: custom (自定义)
   API端点: https://your-company-api.com/v1/chat/completions
   API密钥: your-internal-api-key
   ```

3. **批量输入模型名称**
   
   **单行模式**（用逗号分隔）:
   ```
   company-gpt-4, company-claude, company-llama2, company-qwen
   ```
   
   **批量模式**（每行一个）:
   ```
   company-gpt-4
   company-claude-pro
   company-llama2-70b
   company-qwen-14b
   internal-code-model
   internal-chat-model
   ```

4. **设置通用参数**
   ```
   Temperature: 0.7
   Max Tokens: 2000
   标签: internal, production
   描述: 公司内部部署的大语言模型
   ```

5. **批量创建**
   - 点击"批量创建X个模型"
   - 系统会自动为每个模型创建独立配置
   - 名称格式: `{前缀} - {模型名称}`

### 方法2: 快速设置功能

1. **选择"自定义端点"**
2. **输入企业API端点**
3. **配置API密钥**
4. **选择预设的自定义模型**

## 🔧 企业部署最佳实践

### 1. 命名规范

**推荐的命名格式**:
```
公司名-模型类型-规模
例如: 
- ByteDance-Chat-7B
- Alibaba-Code-13B  
- Tencent-Embedding-Base
```

**批量输入示例**:
```
ByteDance-Chat-7B
ByteDance-Chat-13B
ByteDance-Code-7B
ByteDance-Code-13B
ByteDance-Embedding-Base
```

### 2. 参数配置

**不同用途的参数设置**:

```javascript
// 聊天类模型
{
  "temperature": 0.7,
  "max_tokens": 2000,
  "top_p": 0.9
}

// 代码生成模型  
{
  "temperature": 0.1,
  "max_tokens": 4000,
  "top_p": 0.95
}

// 文本嵌入模型
{
  "temperature": 0.0,
  "max_tokens": 1,
  "dimensions": 1536
}
```

### 3. 标签管理

**建议的标签分类**:
```
环境标签: production, staging, development
模型类型: chat, code, embedding, multimodal
部署方式: internal, cloud, hybrid
性能级别: high-performance, standard, lite
```

**批量设置示例**:
```
标签: internal, production, chat, high-performance
```

## 📋 具体使用示例

### 示例1: 公司聊天机器人模型群

```
场景: 公司内部部署了多个聊天模型，需要批量配置

配置信息:
- API端点: https://chat-api.company.com/v1/completions
- API密钥: internal-key-2024
- 模型前缀: 公司聊天模型

批量输入模型:
ChatBot-GPT4-Pro
ChatBot-Claude3-Sonnet  
ChatBot-GLM4-Turbo
ChatBot-Qwen-Max
ChatBot-Baichuan-Pro

结果: 一次性创建5个聊天模型配置
```

### 示例2: 代码助手模型组

```
场景: 开发团队内部代码生成模型

配置信息:
- API端点: https://code-api.company.com/v1/generate
- 模型前缀: 代码助手

批量输入:
CodeLlama-7B
CodeLlama-13B
CodeLlama-34B
StarCoder-15B
CodeT5-Plus
WizardCoder-15B

标签: internal, code, development
```

### 示例3: 多模态模型服务

```
场景: 公司内部多模态AI服务

批量输入:
MultiModal-Vision-V1
MultiModal-Vision-V2
MultiModal-Audio-V1
MultiModal-Document-Parser
MultiModal-Video-Analyzer

描述: 公司内部多模态AI服务，支持图像、音频、文档处理
```

## 🚀 快速配置脚本

对于大规模部署，也可以使用API直接批量创建：

```bash
#!/bin/bash
# 企业模型批量配置脚本

API_BASE="http://localhost:8000/api/models"
API_KEY="your-internal-api-key"
ENDPOINT="https://your-company-api.com/v1/chat/completions"

MODELS=(
    "company-gpt-4:公司GPT-4模型"
    "company-claude:公司Claude模型" 
    "company-llama2:公司Llama2模型"
    "company-qwen:公司通义千问模型"
)

for model_info in "${MODELS[@]}"; do
    IFS=":" read -r model_name description <<< "$model_info"
    
    curl -X POST "$API_BASE" \
        -H "Content-Type: application/json" \
        -d "{
            \"name\": \"$model_name\",
            \"provider\": \"custom\",
            \"api_endpoint\": \"$ENDPOINT\",
            \"api_key\": \"$API_KEY\",
            \"model_name\": \"$model_name\",
            \"description\": \"$description\",
            \"tags\": \"internal,production\"
        }"
done
```

## 🔒 安全考虑

1. **API密钥管理**: 使用企业密钥管理系统
2. **网络访问**: 确保内网访问安全性
3. **权限控制**: 不同团队使用不同的API密钥
4. **审计日志**: 记录模型使用情况

## 💡 优势总结

1. **灵活性**: 支持任意数量的模型批量添加
2. **标准化**: 统一的配置和命名规范
3. **效率**: 大幅减少手动配置时间
4. **可维护**: 便于后续管理和更新
5. **扩展性**: 支持企业规模的模型部署

这种方式特别适合企业内部有统一API端点但多个模型的场景，让模型配置变得简单高效！
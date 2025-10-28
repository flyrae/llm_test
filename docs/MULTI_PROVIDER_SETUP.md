# 模型服务商批量添加功能 - 使用指南

## 🌟 新增功能亮点

现在支持 **15+ 主流模型服务商**，可以按端点批量添加多个模型！

### 📊 支持的服务商

#### 🌍 国际服务商
- **OpenAI** - GPT-4, GPT-4 Turbo, GPT-4o, GPT-3.5 Turbo 等
- **Anthropic** - Claude 3 Opus/Sonnet/Haiku, Claude 2.1
- **Google Gemini** - Gemini Pro, Gemini Pro Vision, Gemini 1.5 Pro/Flash
- **Azure OpenAI** - Azure 部署的 GPT 模型
- **Together AI** - Llama 2, Mixtral, RedPajama 等开源模型
- **Hugging Face** - DialoGPT, BlenderBot, GPT-J 等
- **Cohere** - Command 系列模型

#### 🇨🇳 国内服务商
- **智谱AI (GLM)** - GLM-4, GLM-4 Air, GLM-3 Turbo, ChatGLM3-6B
- **月之暗面 (Kimi)** - Moonshot v1 8K/32K/128K
- **百川智能** - Baichuan2-Turbo, Baichuan2-Turbo-192k
- **字节跳动 (豆包)** - 豆包 Pro/Lite
- **MiniMax** - ABAB 6/5.5 Chat
- **DeepSeek** - DeepSeek Chat/Coder/Math

#### 🏠 本地部署
- **Ollama** - Llama 2, Code Llama, Mistral, Qwen, ChatGLM3, Baichuan2, DeepSeek Coder, Phi, Gemma, Yi 等

## 🚀 使用方法

### 步骤1: 选择服务商
1. 点击右上角**"快速设置"**按钮
2. 使用**搜索框**快速查找服务商
3. 使用**分类标签**过滤：
   - 全部
   - 国际服务商
   - 国内服务商
   - 本地部署

### 步骤2: 配置连接
- **API密钥**: 云服务商需要提供API密钥
- **API端点**: 可自定义，留空使用默认端点
- **本地模型**: 无需API密钥，只需确保Ollama服务运行

### 步骤3: 选择模型
- 查看该服务商所有可用模型
- 使用**全选/清空**快速操作
- 单独选择需要的模型

### 步骤4: 批量创建
- 显示将创建的模型数量
- 自动处理重名冲突
- 展示创建结果和错误信息

## 📝 使用示例

### 示例1: 快速添加OpenAI全系列模型
```
1. 选择 "OpenAI"
2. 输入API密钥: sk-xxxxx
3. 全选模型 (5个模型)
4. 点击"创建5个模型配置"
```

### 示例2: 添加智谱AI模型
```
1. 选择 "智谱AI (GLM)"
2. 输入API密钥: your-zhipu-key
3. 选择需要的模型 (如GLM-4, GLM-4 Air)
4. 批量创建
```

### 示例3: 本地Ollama模型
```
1. 选择 "本地模型 (Ollama)"
2. 确认端点: http://localhost:11434/api/chat
3. 选择已安装的模型 (如llama2, qwen, mistral)
4. 无需API密钥，直接创建
```

### 示例4: 自定义企业端点
```
1. 选择 "自定义端点"
2. 输入企业内部API端点
3. 配置API密钥
4. 添加自定义模型名称
```

## 🎯 使用场景

### 场景1: 模型对比测试
研究人员想要对比不同厂商的类似模型：
- 快速添加OpenAI GPT-4 + Anthropic Claude 3 Opus + Google Gemini Pro
- 使用相同测试用例进行评估对比

### 场景2: 成本优化
根据不同任务选择合适的模型：
- 简单任务: GPT-3.5 Turbo, Claude 3 Haiku
- 复杂任务: GPT-4, Claude 3 Opus
- 代码任务: Code Llama, DeepSeek Coder

### 场景3: 本地部署评估
评估开源模型在本地的表现：
- 批量添加Llama 2 (7B/13B/70B)
- 对比不同参数规模的效果

### 场景4: 国产化替代
企业评估国产大模型：
- 批量添加智谱、月之暗面、百川等国产模型
- 与国际模型进行对比测试

## 💡 高级功能

### 1. 智能命名
- 自动生成合理的模型配置名称
- 格式: `{服务商} - {模型显示名}`
- 自动处理重名冲突

### 2. 参数继承
- 每个模型都有合适的默认参数
- 支持模型特定的参数覆盖
- 统一的标签管理

### 3. 错误处理
- 详细的错误提示
- 部分成功时的友好反馈
- 重名检测和处理

### 4. 灵活配置
- 支持自定义端点
- 支持企业内网部署
- 支持代理和特殊配置

## 🔮 未来扩展

1. **动态模型发现**: 自动检测端点可用的模型
2. **配置模板保存**: 保存常用的批量配置
3. **参数批量调整**: 批量修改模型参数
4. **分组管理**: 按项目或用途对模型分组
5. **成本监控**: 显示各模型的调用成本

这个功能极大地简化了多模型环境的配置过程，让用户可以快速建立完整的测试环境！
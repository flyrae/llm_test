# LLM 测试工具

一个功能强大的大语言模型测试和评估平台，支持多种模型服务商的批量配置和对比测试。

## ✨ 主要特性

### 🚀 批量模型配置
- **15+ 主流服务商支持** - OpenAI、Anthropic、Google Gemini、智谱AI、月之暗面等
- **一键批量添加** - 从预设模板快速创建多个模型配置
- **智能分类过滤** - 按国际/国内/本地服务商分类
- **搜索功能** - 快速查找特定服务商

### 🧪 模型测试
- **测试用例管理** - 创建和管理测试场景
- **批量测试** - 一次性测试多个模型
- **结果对比** - 可视化对比不同模型的表现
- **评估指标** - 多维度评估模型性能

### 🛠️ 工具集成
- **Function Calling** - 测试模型的工具调用能力
- **系统提示词** - 管理和测试不同的系统提示
- **调试模式** - 详细的请求响应日志

### 📊 数据管理
- **结果存储** - 保存所有测试结果
- **数据导出** - 支持多种格式导出
- **历史记录** - 完整的测试历史追踪

## 🎯 支持的模型服务商

### 🌍 国际服务商
| 服务商 | 模型示例 | 状态 |
|--------|----------|------|
| OpenAI | GPT-4, GPT-4 Turbo, GPT-3.5 | ✅ |
| Anthropic | Claude 3 Opus/Sonnet/Haiku | ✅ |
| Google | Gemini Pro, Gemini Pro Vision | ✅ |
| Azure OpenAI | Azure GPT-4, GPT-3.5 | ✅ |
| Together AI | Llama 2, Mixtral, CodeLlama | ✅ |
| Hugging Face | DialoGPT, BlenderBot, GPT-J | ✅ |
| Cohere | Command, Command Light | ✅ |

### 🇨🇳 国内服务商
| 服务商 | 模型示例 | 状态 |
|--------|----------|------|
| 智谱AI | GLM-4, ChatGLM3 | ✅ |
| 月之暗面 | Moonshot v1 8K/32K/128K | ✅ |
| 百川智能 | Baichuan2-Turbo | ✅ |
| 字节跳动 | 豆包 Pro/Lite | ✅ |
| MiniMax | ABAB 6 Chat | ✅ |
| DeepSeek | DeepSeek Chat/Coder | ✅ |

### 🏠 本地部署
| 平台 | 模型示例 | 状态 |
|------|----------|------|
| Ollama | Llama 2, Mistral, Qwen, CodeLlama | ✅ |
| 自定义 | 企业内部模型服务 | ✅ |

## 🚀 快速开始

### 1. 环境准备
```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动服务
```bash
# 启动后端
cd backend
python -m app.main

# 前端已集成，访问 http://localhost:8000
```

### 3. 快速配置模型

#### 方法1: 使用快速设置功能
1. 访问"模型配置"页面
2. 点击"快速设置"按钮
3. 选择服务商（如OpenAI）
4. 输入API密钥
5. 选择要添加的模型
6. 点击"创建X个模型配置"

#### 方法2: 手动添加
1. 点击"添加模型"
2. 填写模型信息
3. 保存配置

### 4. 创建测试用例
1. 访问"测试用例"页面
2. 创建新的测试场景
3. 添加测试数据和期望结果

### 5. 运行测试
1. 选择要测试的模型
2. 选择测试用例
3. 开始批量测试
4. 查看结果对比

## 📖 使用文档

- [批量模型设置指南](docs/BATCH_MODEL_SETUP.md)
- [多服务商配置指南](docs/MULTI_PROVIDER_SETUP.md)
- [批量导入快速开始](docs/BATCH_IMPORT_QUICKSTART.md)
- [工具页面使用指南](docs/TOOLS_PAGE_USAGE_GUIDE.md)

## 🛠️ 开发指南

### 项目结构
```
llm_test/
├── backend/           # 后端服务
│   ├── app/
│   │   ├── api/       # API路由
│   │   ├── models/    # 数据模型
│   │   ├── services/  # 业务逻辑
│   │   └── utils/     # 工具函数
│   └── data/          # 数据存储
├── frontend/          # 前端界面
│   ├── pages/         # 页面文件
│   ├── assets/        # 静态资源
│   └── index.html     # 主页
└── docs/             # 文档
```

### API 端点
- `GET /api/models/` - 获取模型列表
- `POST /api/models/quick-setup` - 批量创建模型
- `GET /api/models/presets/list` - 获取预设模板
- `GET /api/testcases/` - 获取测试用例
- `POST /api/debug/test` - 运行测试

### 添加新服务商
1. 在 `backend/app/api/models.py` 中的 `PROVIDER_PRESETS` 添加配置
2. 在前端的相关方法中添加显示逻辑
3. 测试API端点连通性

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

[MIT License](LICENSE)

## 🆘 问题反馈

如果您遇到任何问题或有改进建议，请：

1. 查看[文档](docs/)了解详细使用方法
2. 提交 [Issue](https://github.com/your-repo/issues)
3. 联系开发团队

---

**让大模型测试变得简单高效！** 🚀
# 快速开始指南

## 🎯 5分钟快速上手

### 步骤 1: 安装依赖

#### Windows
```powershell
# 使用启动脚本（自动安装依赖）
.\start.ps1
```

#### Linux/Mac
```bash
# 赋予执行权限
chmod +x start.sh

# 运行启动脚本
./start.sh
```

#### 手动安装
```bash
cd backend
pip install -r requirements.txt
```

### 步骤 2: 配置环境变量（可选）

```bash
cd backend
cp .env.example .env
# 编辑 .env 文件，填写必要的配置
```

### 步骤 3: 启动应用

```bash
cd backend
python -m app.main
```

应用将在 `http://localhost:8000` 启动

### 步骤 4: 访问Web界面

打开浏览器访问: `http://localhost:8000`

---

## 📋 基本使用流程

### 1️⃣ 配置模型

1. 点击导航栏的"模型配置"
2. 点击"添加模型"按钮
3. 填写模型信息：
   - **模型名称**: 自定义名称（如"GPT-4测试"）
   - **提供商**: 选择OpenAI、Claude、本地模型或自定义
   - **模型名称**: 填写具体模型（如"gpt-4"、"claude-3-opus"）
   - **API密钥**: 填写对应的API密钥
   - **参数配置**: 设置temperature、max_tokens等参数
4. 点击"添加"保存

**示例配置 - OpenAI GPT-4:**
```
名称: GPT-4
提供商: openai
模型名称: gpt-4
API密钥: sk-your-api-key-here
Temperature: 0.7
Max Tokens: 1000
```

**示例配置 - 本地Ollama:**
```
名称: Llama2本地
提供商: local
模型名称: llama2
API端点: http://localhost:11434
Temperature: 0.7
Max Tokens: 1000
```

### 2️⃣ 创建测试用例

1. 点击"测试用例"
2. 点击"添加用例"
3. 填写测试信息：
   - **标题**: 测试用例的名称
   - **分类**: 可选，用于组织用例
   - **系统提示词**: 可选，定义AI角色
   - **用户提示词**: 必填，实际的测试输入
   - **期望输出**: 可选，用于评估
   - **标签**: 可选，用逗号分隔
4. 点击"添加"保存

**示例测试用例:**
```
标题: 代码解释测试
分类: 编程
系统提示词: 你是一个专业的Python编程助手
用户提示词: 请解释以下代码的作用: print("Hello World")
标签: python, 代码, 基础
```

### 3️⃣ 调试测试

1. 点击"调试"
2. 选择要测试的模型
3. 调整参数（temperature等）
4. 输入提示词
5. 点击"发送"
6. 查看响应和性能指标

### 4️⃣ 批量对比测试

1. 点击"对比测试"
2. 在左侧选择多个模型（勾选复选框）
3. 在右侧选择多个测试用例
4. 点击"开始批量测试"
5. 等待测试完成
6. 查看详细的对比结果
7. 可以导出结果为JSON文件

---

## 🔧 常见配置

### 配置OpenAI模型

```
提供商: openai
模型名称: gpt-3.5-turbo 或 gpt-4
API密钥: 从 https://platform.openai.com/api-keys 获取
API端点: 留空（使用默认）
```

### 配置Claude模型

```
提供商: anthropic
模型名称: claude-3-opus-20240229
API密钥: 从 Anthropic控制台获取
API端点: 留空（使用默认）
```

### 配置本地Ollama模型

1. 先安装Ollama: https://ollama.ai
2. 启动Ollama并下载模型: `ollama pull llama2`
3. 在应用中配置:
```
提供商: local
模型名称: llama2
API端点: http://localhost:11434
API密钥: 留空
```

### 配置兼容OpenAI的自定义API

```
提供商: custom
模型名称: 自定义模型名
API密钥: 你的API密钥
API端点: https://your-api-endpoint.com/v1
```

---

## 📊 批量导入测试用例

### JSON格式导入

创建一个JSON文件 `test_cases.json`:

```json
{
  "test_cases": [
    {
      "title": "数学问题",
      "category": "数学",
      "prompt": "1+1等于几？",
      "tags": "数学,基础"
    },
    {
      "title": "代码生成",
      "category": "编程",
      "prompt": "用Python写一个冒泡排序",
      "system_prompt": "你是编程助手",
      "tags": "python,算法"
    }
  ]
}
```

然后在"测试用例"页面点击"批量导入" -> 选择JSON格式 -> 上传文件

### CSV格式导入

创建一个CSV文件 `test_cases.csv`:

```csv
title,category,prompt,system_prompt,tags
数学问题,数学,1+1等于几？,,数学 基础
代码生成,编程,用Python写一个冒泡排序,你是编程助手,python 算法
```

然后在"测试用例"页面点击"批量导入" -> 选择CSV格式 -> 上传文件

---

## 🎨 界面导航

- **首页**: 概览和快速访问
- **模型配置**: 管理所有LLM模型
- **测试用例**: 创建和管理测试提示词
- **调试**: 单次实时测试
- **对比测试**: 多模型批量对比

---

## 💡 使用技巧

1. **参数调优**: 在调试页面实时调整temperature等参数，观察输出变化
2. **标签管理**: 使用标签组织测试用例，方便筛选
3. **分类组织**: 用分类将相似的测试用例分组
4. **历史记录**: 调试页面会保存最近20条历史，方便重复测试
5. **性能对比**: 使用对比测试功能直观比较不同模型的性能和输出质量
6. **成本估算**: 查看每次调用的token消耗和估算成本

---

## 🚨 常见问题

### Q: 启动失败，提示端口占用
**A:** 修改 `backend/.env` 文件中的 `PORT=8000` 为其他端口

### Q: 调用OpenAI失败
**A:** 检查：
1. API密钥是否正确
2. 是否有足够的余额
3. 网络是否能访问OpenAI

### Q: 本地Ollama连接失败
**A:** 确保：
1. Ollama已启动
2. 模型已下载: `ollama list`
3. 端点正确: `http://localhost:11434`

### Q: 批量测试卡住
**A:** 
1. 检查浏览器控制台是否有错误
2. 刷新页面重试
3. 减少测试数量

---

## 📚 更多资源

- **API文档**: http://localhost:8000/docs
- **GitHub**: 查看完整源代码
- **问题反馈**: 提交Issue

---

**祝使用愉快！🎉**

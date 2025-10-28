# 系统提示词配置功能

## 功能概述

已成功添加系统提示词配置功能，允许你在调试时快速选择和管理常用的系统提示词模板。

## 新增内容

### 1. 数据库
- ✅ 新增 `system_prompts` 表
- ✅ 预置了 8 个默认提示词模板：
  - 通用助手
  - 编程助手
  - 翻译助手
  - 文案写作
  - 数据分析师
  - JSON专家
  - 简洁回答
  - 教学助手

### 2. 后端API
- ✅ `/api/system-prompts/` - 获取所有提示词列表
- ✅ `/api/system-prompts/{id}` - 获取单个提示词
- ✅ `/api/system-prompts/` (POST) - 创建新提示词
- ✅ `/api/system-prompts/{id}` (PUT) - 更新提示词
- ✅ `/api/system-prompts/{id}` (DELETE) - 删除提示词
- ✅ `/api/system-prompts/categories/list` - 获取所有分类

### 3. 前端页面

#### 系统提示词管理页面 (`/pages/system_prompts.html`)
- ✅ 按分类展示所有提示词模板
- ✅ 创建、编辑、删除提示词
- ✅ 分类筛选功能
- ✅ 一键复制提示词内容

#### 调试页面增强 (`/pages/debug.html`)
- ✅ 在系统提示词文本框上方添加下拉选择器
- ✅ 按分类分组显示可用模板
- ✅ 选择模板后自动填充内容
- ✅ 链接到提示词管理页面

#### 主页导航
- ✅ 添加"系统提示词"导航链接
- ✅ 添加功能卡片展示

## 使用方法

### 1. 启动服务器
```powershell
cd backend
conda activate modelscope
python -m uvicorn app.main:app --reload
```

### 2. 访问系统提示词管理
打开浏览器访问：`http://localhost:8000/pages/system_prompts.html`

### 3. 在调试页面使用
1. 访问调试页面：`http://localhost:8000/pages/debug.html`
2. 在"系统提示词"区域，点击下拉框
3. 选择需要的预设模板
4. 提示词内容会自动填充到文本框
5. 可以直接使用或进行修改

## 功能特点

1. **模板管理**
   - 支持创建自定义提示词模板
   - 可按分类组织（通用、编程、翻译等）
   - 添加描述说明用途

2. **快速选择**
   - 下拉框按分类分组显示
   - 一键应用预设模板
   - 支持手动编辑调整

3. **便捷操作**
   - 一键复制提示词内容
   - 编辑和删除模板
   - 分类筛选查看

## 数据库迁移

已执行的迁移脚本：
```bash
cd backend
conda run -n modelscope python migrate_add_system_prompts.py
```

结果：
- ✅ 表创建成功
- ✅ 8 个默认模板已添加

## 文件清单

### 新增文件
- `backend/app/models/system_prompt.py` - 数据模型
- `backend/app/api/system_prompts.py` - API路由
- `backend/migrate_add_system_prompts.py` - 数据库迁移脚本
- `frontend/pages/system_prompts.html` - 管理页面

### 修改文件
- `backend/app/main.py` - 注册新的API路由
- `frontend/pages/debug.html` - 添加提示词选择器（已存在）
- `frontend/index.html` - 添加导航链接（已存在）

## 测试建议

1. 访问系统提示词管理页面，查看预设模板
2. 尝试创建一个新的自定义模板
3. 在调试页面测试选择和使用模板
4. 测试编辑和删除功能
5. 验证分类筛选是否正常工作

## 注意事项

- 系统提示词仅存储模板，不会自动应用到所有测试
- 在调试页面需要手动选择要使用的模板
- 删除提示词模板不会影响已有的测试用例
- 建议为常用的提示词创建模板以提高效率

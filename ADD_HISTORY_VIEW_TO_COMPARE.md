# 为对比页面添加历史测试查看功能

## 问题描述

`compare.html` 页面中，缺少可以直接查看测试历史的地方，每次都需要执行测试才能查看测试历史。

## 解决方案

### 1. 后端改动

在 `backend/app/api/batch.py` 中添加了获取历史批量测试列表的API：

```python
@router.get("/history")
async def get_batch_history():
    """获取所有批量测试历史记录"""
    import os
    from pathlib import Path
    
    results_dir = settings.RESULTS_DIR
    if not results_dir.exists():
        return []
    
    history = []
    for file in sorted(results_dir.glob("batch_*.json"), reverse=True):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                history.append({
                    "batch_id": data.get("batch_id"),
                    "timestamp": data.get("timestamp"),
                    "models": data.get("models", []),
                    "test_cases": data.get("test_cases", []),
                    "total_tests": len(data.get("models", [])) * len(data.get("test_cases", []))
                })
        except Exception as e:
            print(f"Error reading batch file {file}: {e}")
            continue
    
    return history
```

**功能说明**：
- 扫描 `backend/data/results/` 目录下所有批量测试结果文件
- 返回按时间倒序排列的批次列表
- 包含批次ID、时间戳、使用的模型和测试用例等信息

### 2. 前端改动

#### 2.1 UI改动

在 `frontend/pages/compare.html` 中：

1. **添加"查看历史测试"按钮**（在配置面板底部）：
```html
<button @click="showHistoryModal = true; loadHistoryList()" 
        class="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700">
    <i class="fas fa-history mr-2"></i>
    查看历史测试
</button>
```

2. **添加历史测试列表弹窗**：
   - 显示所有历史批量测试记录
   - 每条记录显示：
     - 批次ID（batch_id）
     - 测试时间
     - 使用的模型列表
     - 测试用例列表
     - 总测试次数
   - 操作按钮：
     - "查看"按钮：加载该批次的对比结果
     - "删除"按钮：删除该批次

#### 2.2 JavaScript功能

添加了以下方法：

1. **`loadHistoryList()`**：从后端加载历史批次列表
2. **`loadBatchHistory(batch)`**：点击历史记录后，自动：
   - 设置选中的模型和测试用例
   - 加载该批次的对比结果
   - 关闭历史弹窗
   - 滚动到结果区域
3. **`deleteBatch(batchId)`**：删除指定批次
4. **`formatTimestamp(timestamp)`**：格式化显示时间戳

## 使用方法

### 查看历史测试

1. 打开对比测试页面 `/pages/compare.html`
2. 点击配置面板底部的"查看历史测试"按钮
3. 在弹出的窗口中查看所有历史批量测试记录
4. 点击任意记录的"查看"按钮，即可加载该批次的对比结果

### 删除历史记录

在历史测试列表弹窗中，点击对应记录的"删除"按钮，确认后即可删除。

## 测试验证

1. **API测试**：
```bash
curl http://localhost:8000/api/batch/history
```
返回所有历史批次的JSON数组。

2. **前端测试**：
   - 打开 `http://localhost:8000/pages/compare.html`
   - 点击"查看历史测试"按钮
   - 验证是否显示历史记录列表
   - 点击"查看"按钮，验证是否加载对应批次的结果
   - 点击"删除"按钮，验证是否成功删除批次

## 文件修改清单

1. `backend/app/api/batch.py`：添加 `/api/batch/history` 端点
2. `frontend/pages/compare.html`：
   - 添加"查看历史测试"按钮
   - 添加历史测试列表弹窗
   - 添加相关JavaScript方法

## 效果

现在用户可以：
- ✅ 直接查看所有历史批量测试记录
- ✅ 无需重新执行测试即可查看历史对比结果
- ✅ 快速回顾之前的测试数据
- ✅ 管理（删除）历史测试记录

## 注意事项

1. 历史记录基于 `backend/data/results/` 目录下的JSON文件
2. 删除批次只删除JSON文件，不影响数据库中的原始测试结果记录
3. 历史列表按时间倒序排列，最新的测试记录显示在最前面

## 问题修复

### 初始版本bug
在初始实现时，忘记在Vue的`data()`函数中定义三个必要的变量：
- `showHistoryModal`
- `batchHistory`
- `loadingHistory`

这导致点击"查看历史测试"按钮后，弹窗一直显示"加载历史记录中..."状态。

**已修复**：在data()中正确添加了这三个变量的初始化。

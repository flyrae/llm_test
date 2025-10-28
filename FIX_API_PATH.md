# API.js 路径修复

## 问题
系统提示词管理页面 (`system_prompts.html`) 中引用了错误的API工具文件路径：
- ❌ 错误：`/assets/js/api.js`
- ✅ 正确：`/assets/js/utils/api.js`

## 修复内容
已更新 `frontend/pages/system_prompts.html` 中的脚本引用路径。

## 修复前
```html
<script src="/assets/js/api.js"></script>
```

## 修复后
```html
<script src="/assets/js/utils/api.js"></script>
```

## 验证
- ✅ 其他页面均使用正确路径 `/assets/js/utils/api.js`
- ✅ API工具文件位于：`frontend/assets/js/utils/api.js`

## 现在可以
1. 刷新浏览器页面
2. 访问 `http://localhost:8000/pages/system_prompts.html`
3. 不再出现 404 错误
4. 可以正常加载和管理系统提示词

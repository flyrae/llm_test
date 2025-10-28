# 离线环境部署指南

## 概述

本项目已配置为可在离线环境中运行。所有前端依赖已从CDN改为本地文件。

## 前端依赖

项目使用以下前端库：

### 1. Vue.js 3.3.4
- **路径**: `/assets/vendor/vue/`
- **文件**:
  - `vue.global.js` - 开发版本（包含警告和调试信息）
  - `vue.global.prod.js` - 生产版本（优化过的版本，推荐生产环境使用）

### 2. Tailwind CSS (Play CDN)
- **路径**: `/assets/vendor/tailwind/`
- **文件**: `tailwind.js`
- **说明**: 使用Tailwind CSS的Play CDN离线版本，支持JIT编译

### 3. Font Awesome 6.4.0
- **路径**: `/assets/vendor/fontawesome/`
- **文件**:
  - `all.min.css` - CSS样式文件
  - `webfonts/` - 字体文件目录
    - `fa-solid-900.woff2` - Solid图标字体
    - `fa-regular-400.woff2` - Regular图标字体
    - `fa-brands-400.woff2` - Brands图标字体

## 目录结构

```
frontend/
  assets/
    vendor/
      vue/
        vue.global.js           # Vue.js开发版
        vue.global.prod.js      # Vue.js生产版
      tailwind/
        tailwind.js             # Tailwind CSS
      fontawesome/
        all.min.css             # Font Awesome CSS
        webfonts/
          fa-solid-900.woff2
          fa-regular-400.woff2
          fa-brands-400.woff2
    css/
      style.css
    js/
      utils/
        api.js
  index.html
  pages/
    models.html
    testcases.html
    tools.html
    debug.html
    compare.html
```

## HTML引用方式

所有HTML文件都使用本地路径引用依赖：

```html
<script src="/assets/vendor/vue/vue.global.js"></script>
<script src="/assets/vendor/tailwind/tailwind.js"></script>
<link rel="stylesheet" href="/assets/vendor/fontawesome/all.min.css">
```

## 生产环境优化

### 使用Vue.js生产版本

在生产环境中，建议将Vue.js改为生产版本以获得更好的性能：

```html
<!-- 将 vue.global.js 改为 vue.global.prod.js -->
<script src="/assets/vendor/vue/vue.global.prod.js"></script>
```

### 批量替换

可以使用以下PowerShell命令批量替换所有HTML文件：

```powershell
# 在项目根目录执行
Get-ChildItem frontend -Recurse -Include *.html | ForEach-Object {
    (Get-Content $_.FullName -Raw) `
        -replace 'vue\.global\.js', 'vue.global.prod.js' |
    Set-Content $_.FullName
}
```

## 更新依赖

### 更新Vue.js

```powershell
Invoke-WebRequest -Uri "https://cdn.jsdelivr.net/npm/vue@3.3.4/dist/vue.global.prod.js" `
    -OutFile "frontend\assets\vendor\vue\vue.global.prod.js"
```

### 更新Tailwind CSS

```powershell
Invoke-WebRequest -Uri "https://cdn.tailwindcss.com" `
    -OutFile "frontend\assets\vendor\tailwind\tailwind.js"
```

### 更新Font Awesome

```powershell
# 更新CSS
Invoke-WebRequest -Uri "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" `
    -OutFile "frontend\assets\vendor\fontawesome\all.min.css"

# 更新字体文件（注意：字体文件必须放在webfonts子目录中）
Invoke-WebRequest -Uri "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-solid-900.woff2" `
    -OutFile "frontend\assets\vendor\fontawesome\webfonts\fa-solid-900.woff2"

Invoke-WebRequest -Uri "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-regular-400.woff2" `
    -OutFile "frontend\assets\vendor\fontawesome\webfonts\fa-regular-400.woff2"

Invoke-WebRequest -Uri "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-brands-400.woff2" `
    -OutFile "frontend\assets\vendor\fontawesome\webfonts\fa-brands-400.woff2"
```

**重要提示**: Font Awesome的字体文件必须放在 `webfonts` 子目录中，因为CSS文件中使用相对路径 `../webfonts/` 来引用字体文件。

## 离线部署检查清单

- [x] 所有前端依赖已下载到本地
- [x] 所有HTML文件已更新为本地路径
- [x] Font Awesome字体文件已正确放置
- [x] CSS文件中的字体路径使用相对路径
- [ ] （可选）在生产环境切换到Vue.js生产版本

## 验证

启动后端服务器后，在浏览器中访问应用：

```bash
cd backend
python -m uvicorn app.main:app --reload
```

打开浏览器访问 `http://localhost:8000`，检查：

1. 页面样式是否正常显示（Tailwind CSS）
2. 图标是否正常显示（Font Awesome）
3. Vue.js功能是否正常工作
4. 浏览器控制台是否有404错误

## 故障排查

### 样式不显示

- 检查浏览器控制台是否有404错误
- 确认文件路径是否正确
- 确认后端静态文件服务是否正常

### 图标不显示

- 检查Font Awesome的CSS和字体文件是否都已下载
- 确认CSS文件中的webfonts路径是否正确（应为相对路径）
- 检查浏览器控制台的网络请求

### Vue.js不工作

- 确认vue.global.js文件是否完整下载
- 检查浏览器控制台是否有JavaScript错误
- 确认HTML文件中的script标签路径是否正确

## 注意事项

1. **Tailwind CSS JIT模式**: 当前使用的Tailwind CSS Play CDN版本支持JIT编译，但性能可能不如完整编译版本
2. **浏览器兼容性**: Vue 3和现代CSS特性需要较新的浏览器版本
3. **文件完整性**: 确保所有vendor文件都已完整下载，避免文件损坏
4. **路径一致性**: 所有路径都使用`/assets/vendor/`开头，确保与后端静态文件服务配置一致

## 附加优化建议

### 使用完整编译的Tailwind CSS

如果需要更好的性能，可以考虑：

1. 安装Node.js和Tailwind CSS
2. 创建tailwind.config.js配置文件
3. 编译生成完整的CSS文件
4. 替换Play CDN版本

### 启用压缩

在生产环境中，考虑：

1. 对CSS和JS文件进行Gzip压缩
2. 使用CDN加速（如果有内网CDN）
3. 启用浏览器缓存

## 许可证

- **Vue.js**: MIT License
- **Tailwind CSS**: MIT License
- **Font Awesome Free**: CC BY 4.0 (Icons), SIL OFL 1.1 (Fonts), MIT (Code)

/**
 * API工具类 - 统一的HTTP请求封装
 */
const API_BASE_URL = '';

/**
 * 确保URL格式正确（解决FastAPI重定向问题）
 * 只对资源列表端点（如 /api/models）添加尾部斜杠
 * 对子路由（如 /api/batch/run）不添加斜杠
 */
function normalizeUrl(url) {
    // 如果URL包含查询参数或已经以斜杠结尾，直接返回
    if (url.includes('?') || url.endsWith('/')) {
        return url;
    }
    
    // 只对资源列表端点添加斜杠：/api/xxx 但不包含 /api/xxx/yyy
    // 例如：/api/models -> /api/models/
    //      /api/batch/run -> /api/batch/run (不添加)
    const pathParts = url.split('/').filter(p => p);
    // 如果路径只有2部分（api 和 resource），添加斜杠
    if (pathParts.length === 2 && pathParts[0] === 'api') {
        return url + '/';
    }
    
    return url;
}

const api = {
    /**
     * GET请求
     */
    async get(url, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const normalizedUrl = normalizeUrl(url);
        const fullUrl = `${API_BASE_URL}${normalizedUrl}${queryString ? '?' + queryString : ''}`;
        
        const response = await fetch(fullUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    },

    /**
     * POST请求
     */
    async post(url, data = {}) {
        const normalizedUrl = normalizeUrl(url);
        const response = await fetch(`${API_BASE_URL}${normalizedUrl}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || `HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    },

    /**
     * PUT请求
     */
    async put(url, data = {}) {
        const normalizedUrl = normalizeUrl(url);
        const response = await fetch(`${API_BASE_URL}${normalizedUrl}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || `HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    },

    /**
     * DELETE请求
     */
    async delete(url) {
        const normalizedUrl = normalizeUrl(url);
        const response = await fetch(`${API_BASE_URL}${normalizedUrl}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return response.status === 204 ? null : await response.json();
    },

    /**
     * 文件上传
     */
    async upload(url, file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const normalizedUrl = normalizeUrl(url);
        const response = await fetch(`${API_BASE_URL}${normalizedUrl}`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
};

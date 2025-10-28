#!/usr/bin/env python3
"""
快速测试DashScope模型获取功能
"""
import requests
import json

# 从.env文件读取配置
def load_env():
    config = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    config[key] = value
    except FileNotFoundError:
        print("⚠️  .env文件未找到，使用默认配置")
    return config

def test_dashscope_models():
    """测试DashScope模型获取"""
    config = load_env()
    api_key = config.get('API_KEY', 'sk-c3868d72ebe54f93bf203742c4e2fd46')
    endpoint = config.get('ENDPOINT', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
    
    print(f"🧪 测试DashScope模型获取")
    print(f"   端点: {endpoint}")
    print(f"   API密钥: {api_key[:10]}...")
    
    # 测试不同的端点格式
    test_endpoints = [
        endpoint,
        endpoint.rstrip('/') + '/models',  # 直接models端点
        endpoint.rstrip('/') + '/chat/completions'  # chat端点
    ]
    
    for test_endpoint in test_endpoints:
        print(f"\n📡 测试端点: {test_endpoint}")
        
        request_data = {
            "api_endpoint": test_endpoint,
            "api_key": api_key,
            "provider": "custom"
        }
        
        try:
            response = requests.post(
                "http://localhost:8008/api/models/fetch-models",
                json=request_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    print(f"✅ 成功! 转换为: {data['endpoint']}")
                    print(f"   获取到 {data['total']} 个模型:")
                    for i, model in enumerate(data['models'][:5]):
                        print(f"     {i+1}. {model['id']}")
                    if len(data['models']) > 5:
                        print(f"     ... 还有 {len(data['models']) - 5} 个")
                    return data['models']
                else:
                    print(f"❌ 失败: {data['error']}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
    
    return []

def test_manual_curl():
    """提供手动curl测试命令"""
    config = load_env()
    api_key = config.get('API_KEY', 'sk-c3868d72ebe54f93bf203742c4e2fd46')
    endpoint = config.get('ENDPOINT', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
    
    models_endpoint = endpoint.rstrip('/') + '/models'
    
    print(f"\n🔧 手动测试命令:")
    print(f"curl -H 'Authorization: Bearer {api_key}' \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     '{models_endpoint}'")

if __name__ == "__main__":
    print("🚀 DashScope模型获取测试\n")
    
    # 测试API
    models = test_dashscope_models()
    
    # 提供手动测试方法
    test_manual_curl()
    
    print("\n📊 测试完成")
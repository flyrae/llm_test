#!/usr/bin/env python3
"""
测试从端点获取模型列表功能
"""
import requests
import json

# 配置
BASE_URL = "http://localhost:8008"

def test_fetch_dashscope_models():
    """测试从DashScope获取模型列表"""
    print("🧪 测试从DashScope获取模型列表...")
    
    request_data = {
        "api_endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "api_key": "sk-c3868d72ebe54f93bf203742c4e2fd46",
        "provider": "custom"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/models/fetch-models",
        json=request_data
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"✅ 成功获取 {data['total']} 个模型")
            print(f"   端点: {data['endpoint']}")
            
            if data['models']:
                print("   模型列表:")
                for i, model in enumerate(data['models'][:10]):  # 只显示前10个
                    print(f"     {i+1}. {model['id']} ({model.get('owned_by', 'unknown')})")
                
                if len(data['models']) > 10:
                    print(f"     ... 还有 {len(data['models']) - 10} 个模型")
            
            return data['models']
        else:
            print(f"❌ 获取失败: {data['error']}")
            return []
    else:
        print(f"❌ 请求失败: {response.status_code} - {response.text}")
        return []

def test_fetch_openai_models():
    """测试从OpenAI获取模型列表（需要有效的API密钥）"""
    print("\n🧪 测试从OpenAI获取模型列表...")
    
    request_data = {
        "api_endpoint": "https://api.openai.com/v1",
        "api_key": "sk-test-key",  # 这里需要替换为真实的API密钥
        "provider": "openai"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/models/fetch-models",
        json=request_data
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"✅ 成功获取 {data['total']} 个模型")
            return data['models']
        else:
            print(f"⚠️  获取失败（可能是API密钥问题）: {data['error']}")
            return []
    else:
        print(f"❌ 请求失败: {response.status_code}")
        return []

def test_fetch_local_ollama():
    """测试从本地Ollama获取模型列表"""
    print("\n🧪 测试从本地Ollama获取模型列表...")
    
    request_data = {
        "api_endpoint": "http://localhost:11434",
        "api_key": "",
        "provider": "local"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/models/fetch-models",
        json=request_data
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"✅ 成功获取 {data['total']} 个本地模型")
            return data['models']
        else:
            print(f"⚠️  获取失败（可能Ollama未运行）: {data['error']}")
            return []
    else:
        print(f"❌ 请求失败: {response.status_code}")
        return []

def test_batch_create_from_fetched():
    """测试使用获取的模型批量创建配置"""
    print("\n🧪 测试批量创建模型配置...")
    
    # 首先获取DashScope的模型列表
    models = test_fetch_dashscope_models()
    
    if not models:
        print("❌ 无法获取模型列表，跳过批量创建测试")
        return
    
    # 选择前3个模型进行测试
    test_models = models[:3]
    
    for model in test_models:
        try:
            model_config = {
                "name": f"DashScope - {model['display_name']}",
                "provider": "custom",
                "api_endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                "api_key": "sk-c3868d72ebe54f93bf203742c4e2fd46",
                "model_name": model['id'],
                "tags": "dashscope, test",
                "description": f"从DashScope自动获取的模型: {model['description']}"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/models/",
                json=model_config
            )
            
            if response.status_code == 201:
                print(f"✅ 成功创建模型配置: {model['id']}")
            else:
                print(f"⚠️  创建失败: {model['id']} - {response.text}")
                
        except Exception as e:
            print(f"❌ 创建异常: {model['id']} - {e}")

def main():
    """运行所有测试"""
    print("🚀 开始测试模型获取功能\n")
    
    tests = [
        test_fetch_dashscope_models,
        test_fetch_openai_models,
        test_fetch_local_ollama,
        test_batch_create_from_fetched
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    print("\n📊 测试完成")

if __name__ == "__main__":
    main()
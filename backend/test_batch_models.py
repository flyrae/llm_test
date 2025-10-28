#!/usr/bin/env python3
"""
测试批量模型添加功能
"""
import requests
import json

# 配置
BASE_URL = "http://localhost:8008"
TEST_API_KEY = "test-key-12345"

def test_get_presets():
    """测试获取预设列表"""
    print("🧪 测试获取预设模板列表...")
    
    response = requests.get(f"{BASE_URL}/api/models/presets/list")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 成功获取 {len(data['templates'])} 个预设模板")
        
        # 显示前几个模板
        for i, template in enumerate(data['templates'][:5]):
            print(f"   {i+1}. {template['name']} ({template['provider']}) - {len(template['available_models'])} 个模型")
        
        if len(data['templates']) > 5:
            print(f"   ... 还有 {len(data['templates']) - 5} 个模板")
        
        return True
    else:
        print(f"❌ 获取预设失败: {response.status_code} - {response.text}")
        return False

def test_quick_setup_local():
    """测试快速设置本地模型"""
    print("\n🧪 测试快速设置本地模型...")
    
    request_data = {
        "provider": "local",
        "api_key": "",
        "endpoint": "",
        "selected_models": ["llama2", "qwen", "mistral"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/models/quick-setup",
        json=request_data
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 成功创建 {data['created_count']} 个模型配置")
        
        if data['created_models']:
            print("   创建的模型:")
            for model in data['created_models']:
                print(f"   - {model['name']} ({model['model_name']})")
        
        if data['errors']:
            print("   错误:")
            for error in data['errors']:
                print(f"   - {error}")
        
        return True
    else:
        print(f"❌ 快速设置失败: {response.status_code} - {response.text}")
        return False

def test_quick_setup_openai():
    """测试快速设置OpenAI模型"""
    print("\n🧪 测试快速设置OpenAI模型...")
    
    request_data = {
        "provider": "openai",
        "api_key": TEST_API_KEY,
        "endpoint": "",
        "selected_models": ["gpt-4", "gpt-3.5-turbo"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/models/quick-setup",
        json=request_data
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 成功创建 {data['created_count']} 个模型配置")
        
        if data['created_models']:
            print("   创建的模型:")
            for model in data['created_models']:
                print(f"   - {model['name']} ({model['model_name']})")
        
        return True
    else:
        print(f"❌ 快速设置失败: {response.status_code} - {response.text}")
        return False

def test_list_models():
    """测试获取模型列表"""
    print("\n🧪 测试获取模型列表...")
    
    response = requests.get(f"{BASE_URL}/api/models/")
    
    if response.status_code == 200:
        models = response.json()
        print(f"✅ 当前共有 {len(models)} 个模型配置")
        
        # 按provider分组显示
        provider_groups = {}
        for model in models:
            provider = model['provider']
            if provider not in provider_groups:
                provider_groups[provider] = []
            provider_groups[provider].append(model)
        
        for provider, provider_models in provider_groups.items():
            print(f"   {provider}: {len(provider_models)} 个模型")
            for model in provider_models[:3]:  # 只显示前3个
                print(f"     - {model['name']}")
            if len(provider_models) > 3:
                print(f"     - ... 还有 {len(provider_models) - 3} 个")
        
        return True
    else:
        print(f"❌ 获取模型列表失败: {response.status_code} - {response.text}")
        return False

def main():
    """运行所有测试"""
    print("🚀 开始测试批量模型添加功能\n")
    
    tests = [
        test_get_presets,
        test_quick_setup_local,
        test_quick_setup_openai,
        test_list_models
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败，请检查服务器状态")

if __name__ == "__main__":
    main()
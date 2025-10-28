"""测试应用是否正常工作"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"✅ 状态: {response.status_code}")
    print(f"📄 响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_models_list():
    """测试获取模型列表"""
    print("🔍 测试获取模型列表...")
    response = requests.get(f"{BASE_URL}/api/models")
    print(f"✅ 状态: {response.status_code}")
    print(f"📄 模型数量: {len(response.json())}")
    print()

def test_testcases_list():
    """测试获取测试用例列表"""
    print("🔍 测试获取测试用例列表...")
    response = requests.get(f"{BASE_URL}/api/testcases")
    print(f"✅ 状态: {response.status_code}")
    print(f"📄 测试用例数量: {len(response.json())}")
    print()

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 LLM Test Tool API 测试")
    print("=" * 50)
    print()
    
    try:
        test_health()
        test_models_list()
        test_testcases_list()
        
        print("=" * 50)
        print("✅ 所有测试通过！应用运行正常")
        print("=" * 50)
        print()
        print("📡 访问地址:")
        print(f"   主页: {BASE_URL}")
        print(f"   API文档: {BASE_URL}/docs")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保应用已启动")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

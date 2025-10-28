"""快速测试API端点"""
import requests

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("🧪 测试 LLM Test Tool API")
print("=" * 60)
print()

# 测试1: 健康检查
print("1️⃣ 测试健康检查 (/api/health)")
try:
    resp = requests.get(f"{BASE_URL}/api/health")
    print(f"   状态码: {resp.status_code}")
    print(f"   响应: {resp.json()}")
    print("   ✅ 通过")
except Exception as e:
    print(f"   ❌ 失败: {e}")
print()

# 测试2: 获取模型列表 (带斜杠)
print("2️⃣ 测试获取模型列表 (/api/models/)")
try:
    resp = requests.get(f"{BASE_URL}/api/models/")
    print(f"   状态码: {resp.status_code}")
    print(f"   模型数量: {len(resp.json())}")
    print("   ✅ 通过")
except Exception as e:
    print(f"   ❌ 失败: {e}")
print()

# 测试3: 获取模型列表 (不带斜杠)
print("3️⃣ 测试获取模型列表 (/api/models - 不带斜杠)")
try:
    resp = requests.get(f"{BASE_URL}/api/models", allow_redirects=True)
    print(f"   状态码: {resp.status_code}")
    print(f"   模型数量: {len(resp.json())}")
    print("   ✅ 通过")
except Exception as e:
    print(f"   ❌ 失败: {e}")
print()

# 测试4: 获取测试用例列表
print("4️⃣ 测试获取测试用例列表 (/api/testcases/)")
try:
    resp = requests.get(f"{BASE_URL}/api/testcases/")
    print(f"   状态码: {resp.status_code}")
    print(f"   测试用例数量: {len(resp.json())}")
    print("   ✅ 通过")
except Exception as e:
    print(f"   ❌ 失败: {e}")
print()

print("=" * 60)
print("🎯 测试完成！")
print()
print("💡 提示:")
print("   - 使用 /api/models/ (带斜杠) 访问API")
print("   - 或者在前端代码中允许自动重定向")
print("=" * 60)

#!/usr/bin/env python3
"""
测试 Google Search API 配置的脚本
"""

import os
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_google_search_config():
    """测试 Google Search API 配置"""
    
    # 获取环境变量
    api_key = os.getenv("GOOGLE_API_KEY")
    cx = os.getenv("GOOGLE_CX")
    
    print("=== Google Search API 配置测试 ===")
    
    # 检查环境变量
    if not api_key:
        print("❌ GOOGLE_API_KEY 未设置")
        return False
    else:
        print(f"✅ GOOGLE_API_KEY: {api_key[:10]}...")
    
    if not cx:
        print("❌ GOOGLE_CX 未设置")
        return False
    else:
        print(f"✅ GOOGLE_CX: {cx}")
    
    # 测试 API 调用
    print("\n=== 测试 API 调用 ===")
    
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": cx,
            "q": "test search",
            "num": 1
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if "items" in result:
                print("✅ API 调用成功！")
                print(f"   找到 {len(result['items'])} 个搜索结果")
                print(f"   第一个结果: {result['items'][0]['title']}")
                return True
            else:
                print("⚠️ API 调用成功但没有返回搜索结果")
                return True
        else:
            print(f"❌ API 调用失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API 调用出错: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_google_search_config()
    if success:
        print("\n🎉 Google Search API 配置正确！")
    else:
        print("\n❌ Google Search API 配置有问题，请检查上述错误信息") 
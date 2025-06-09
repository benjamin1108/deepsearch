#!/usr/bin/env python3
"""测试API keys配置和LLM提供商可用性"""

import os
from pathlib import Path
from agent.llm_factory import LLMFactory
from agent.search_utils import SearchUtils

# 尝试加载.env文件
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ 已加载 .env 文件: {env_path}")
    else:
        print(f"❌ .env 文件不存在: {env_path}")
except ImportError:
    print("⚠️  python-dotenv 未安装，尝试直接读取环境变量")

def main():
    print("=" * 60)
    print("API Keys 和 LLM 提供商配置测试")
    print("=" * 60)
    
    # 检查LLM API Keys
    print("\n🔑 LLM提供商API Keys检查:")
    llm_keys = [
        ('GEMINI_API_KEY', 'Google Gemini'),
        ('OPENAI_API_KEY', 'OpenAI'), 
        ('DASHSCOPE_API_KEY', 'Qwen/通义千问'),
        ('XAI_API_KEY', 'Grok')
    ]
    
    for key, name in llm_keys:
        value = os.getenv(key)
        if value:
            masked_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else value
            print(f"  ✅ {name}: {key} = {masked_value}")
        else:
            print(f"  ❌ {name}: {key} 未设置")
    
    # 检查搜索API Keys
    print("\n🔍 搜索API Keys检查:")
    search_keys = [
        ('GOOGLE_API_KEY', 'Google Search API'),
        ('GOOGLE_CX', 'Google Custom Search Engine ID'),
        ('SERPAPI_API_KEY', 'SerpAPI'),
        ('BING_SEARCH_API_KEY', 'Bing Search API')
    ]
    
    for key, name in search_keys:
        value = os.getenv(key)
        if value:
            masked_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else value
            print(f"  ✅ {name}: {key} = {masked_value}")
        else:
            print(f"  ❌ {name}: {key} 未设置")
    
    # 检查LLM提供商可用性
    print("\n🤖 LLM提供商可用性检查:")
    providers = ['gemini', 'openai', 'qwen', 'grok']
    
    for provider in providers:
        is_available, error = LLMFactory.check_provider_availability(provider)
        if is_available:
            print(f"  ✅ {provider}: 可用")
        else:
            print(f"  ❌ {provider}: {error}")
    
    # 检查搜索API可用性
    print("\n🔍 搜索API可用性检查:")
    available_apis = SearchUtils.get_available_search_apis()
    if available_apis:
        print(f"  ✅ 可用的搜索APIs: {available_apis}")
    else:
        print(f"  ❌ 没有配置任何搜索API")
    
    # 测试可用的LLM创建
    print("\n🧪 LLM创建测试:")
    for provider in providers:
        is_available, error = LLMFactory.check_provider_availability(provider)
        if is_available:
            try:
                # 使用默认模型测试创建
                from agent.configuration import Configuration
                config = Configuration(llm_provider=provider)
                llm = LLMFactory.create_llm(provider, config.query_generator_model)
                print(f"  ✅ {provider}: 模型创建成功 ({type(llm).__name__})")
            except Exception as e:
                print(f"  ❌ {provider}: 模型创建失败 - {str(e)}")
        else:
            print(f"  ⏭️  {provider}: 跳过测试 (不可用)")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    main() 
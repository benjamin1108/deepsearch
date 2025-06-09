#!/usr/bin/env python3
"""测试配置参数传递流程"""

from dotenv import load_dotenv
load_dotenv()

from agent.configuration import Configuration
from agent.llm_factory import LLMFactory

def test_config_flow():
    print("=" * 60)
    print("测试配置参数传递流程")
    print("=" * 60)
    
    # 模拟前端传递的配置（类似App.tsx中的参数）
    mock_config = {
        "llm_provider": "qwen",
        "query_generator_model": "qwen-plus",
        "reflection_model": "qwen-max",
        "answer_model": "qwen-max",
        "initial_search_query_count": 3,
        "max_research_loops": 3
    }
    
    print("\n🔧 模拟前端传递的配置:")
    for key, value in mock_config.items():
        print(f"  {key}: {value}")
    
    # 测试Configuration.from_runnable_config
    print("\n📋 测试Configuration.from_runnable_config:")
    try:
        config = Configuration.from_runnable_config(mock_config)
        print(f"  ✅ 创建Configuration成功")
        print(f"  Provider: {config.llm_provider}")
        print(f"  Query Model: {config.query_generator_model}")
        print(f"  Reflection Model: {config.reflection_model}")
        print(f"  Answer Model: {config.answer_model}")
    except Exception as e:
        print(f"  ❌ 创建Configuration失败: {e}")
        return
    
    # 测试LLM创建
    print("\n🤖 测试LLM创建:")
    try:
        llm = LLMFactory.create_llm(
            provider=config.llm_provider,
            model_name=config.query_generator_model,
            temperature=0.0,
            max_retries=2
        )
        print(f"  ✅ LLM创建成功: {type(llm).__name__}")
        print(f"  Provider: {config.llm_provider}")
        print(f"  Model: {config.query_generator_model}")
    except Exception as e:
        print(f"  ❌ LLM创建失败: {e}")
    
    # 测试默认Gemini配置（问题场景）
    print("\n⚠️  测试默认Gemini配置（问题场景）:")
    try:
        default_config = Configuration()  # 默认配置
        print(f"  默认Provider: {default_config.llm_provider}")
        print(f"  默认Query Model: {default_config.query_generator_model}")
        
        # 尝试创建Gemini LLM（这里应该会失败，因为位置限制）
        gemini_llm = LLMFactory.create_llm(
            provider=default_config.llm_provider,
            model_name=default_config.query_generator_model,
            temperature=0.0,
            max_retries=2
        )
        print(f"  ✅ Gemini LLM创建成功: {type(gemini_llm).__name__}")
    except Exception as e:
        print(f"  ❌ Gemini LLM创建失败: {e}")
        print(f"     这说明问题可能出现在这里！")

if __name__ == "__main__":
    test_config_flow() 
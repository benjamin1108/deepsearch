#!/usr/bin/env python3
"""端到端测试qwen提供商的查询流程"""

from dotenv import load_dotenv
load_dotenv()

import asyncio
from langchain_core.messages import HumanMessage
from agent.graph import graph

async def test_qwen_end_to_end():
    print("=" * 60)
    print("端到端测试 - Qwen提供商查询流程")
    print("=" * 60)
    
    # 模拟前端传递的配置（直接在config顶层，而不是configurable中）
    config = {
        "llm_provider": "qwen",
        "query_generator_model": "qwen-plus",
        "reflection_model": "qwen-max", 
        "answer_model": "qwen-max",
        "number_of_initial_queries": 1,
        "max_research_loops": 1
    }
    
    # 构建测试消息
    test_question = "什么是人工智能？请简要介绍。"
    messages = [HumanMessage(content=test_question)]
    
    print(f"\n📝 测试问题: {test_question}")
    print(f"\n🔧 使用配置:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    print(f"\n🚀 开始执行查询流程...")
    
    try:
        # 运行图
        result = await graph.ainvoke(
            {"messages": messages},
            config=config
        )
        
        print(f"\n✅ 查询执行成功!")
        print(f"\n📄 结果:")
        if result.get("messages"):
            for msg in result["messages"]:
                if hasattr(msg, 'content'):
                    print(f"  {msg.content[:200]}...")
        
        print(f"\n📚 收集的源:")
        if result.get("sources_gathered"):
            for i, source in enumerate(result["sources_gathered"][:3], 1):
                print(f"  {i}. {source.get('label', 'Unknown')}: {source.get('snippet', 'No snippet')[:100]}...")
        
    except Exception as e:
        print(f"\n❌ 查询执行失败: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
        import traceback
        traceback.print_exc()

def main():
    """运行测试"""
    try:
        asyncio.run(test_qwen_end_to_end())
    except KeyboardInterrupt:
        print("\n\n中断测试")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")

if __name__ == "__main__":
    main() 
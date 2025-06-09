#!/usr/bin/env python3
"""测试qwen模型的结构化输出功能"""

from dotenv import load_dotenv
load_dotenv()

from agent.llm_factory import LLMFactory
from agent.tools_and_schemas import SearchQueryList, Reflection

def test_qwen_structured_output():
    print("=" * 60)
    print("测试Qwen模型的结构化输出功能")
    print("=" * 60)
    
    try:
        # 创建qwen LLM
        llm = LLMFactory.create_llm(
            provider="qwen",
            model_name="qwen-plus",
            temperature=0.5,
            max_retries=2
        )
        print("✅ Qwen LLM创建成功")
        
        # 测试简单的文本输出
        print("\n📝 测试简单文本输出:")
        simple_prompt = "请用一句话解释什么是人工智能"
        simple_result = llm.invoke(simple_prompt)
        print(f"  结果: {simple_result.content[:100]}...")
        
        # 测试SearchQueryList结构化输出
        print("\n🔍 测试SearchQueryList结构化输出:")
        structured_llm = llm.with_structured_output(SearchQueryList)
        
        search_prompt = """为了研究"人工智能的发展历史"这个主题，请生成2个相关的搜索查询。

请按照以下格式返回JSON:
{
    "query": ["查询1", "查询2"],
    "rationale": "为什么选择这些查询的原因"
}
"""
        
        try:
            search_result = structured_llm.invoke(search_prompt)
            if search_result is None:
                print("  ❌ 结构化输出返回None")
            else:
                print(f"  ✅ 结构化输出成功")
                print(f"  查询列表: {search_result.query}")
                print(f"  理由: {search_result.rationale}")
        except Exception as e:
            print(f"  ❌ 结构化输出失败: {e}")
            print(f"  错误类型: {type(e).__name__}")
        
        # 测试Reflection结构化输出
        print("\n🤔 测试Reflection结构化输出:")
        reflection_llm = llm.with_structured_output(Reflection)
        
        reflection_prompt = """基于以下总结，判断是否需要更多信息：

总结：人工智能是一种计算机科学技术。

请按照以下格式返回JSON:
{
    "is_sufficient": true/false,
    "knowledge_gap": "缺少的信息描述",
    "follow_up_queries": ["后续查询1", "后续查询2"]
}
"""
        
        try:
            reflection_result = reflection_llm.invoke(reflection_prompt)
            if reflection_result is None:
                print("  ❌ Reflection结构化输出返回None")
            else:
                print(f"  ✅ Reflection结构化输出成功")
                print(f"  是否足够: {reflection_result.is_sufficient}")
                print(f"  知识缺口: {reflection_result.knowledge_gap}")
                print(f"  后续查询: {reflection_result.follow_up_queries}")
        except Exception as e:
            print(f"  ❌ Reflection结构化输出失败: {e}")
            print(f"  错误类型: {type(e).__name__}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_qwen_structured_output() 
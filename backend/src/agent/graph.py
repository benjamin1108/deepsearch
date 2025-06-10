import os

from agent.tools_and_schemas import SearchQueryList, Reflection
from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import AIMessage
from langgraph.types import Send
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig

from agent.state import (
    OverallState,
    QueryGenerationState,
    ReflectionState,
    WebSearchState,
)
from agent.configuration import Configuration
from agent.prompts import (
    get_current_date,
    query_writer_instructions,
    web_searcher_instructions,
    reflection_instructions,
    answer_instructions,
)
from agent.llm_factory import LLMFactory
from agent.search_utils import SearchUtils
from agent.utils import (
    get_citations,
    get_research_topic,
    insert_citation_markers,
    resolve_urls,
)


# Nodes
def generate_query(state: OverallState, config: RunnableConfig) -> QueryGenerationState:
    """LangGraph 节点，根据用户的问题生成搜索查询。

    使用 Gemini 2.0 Flash 根据用户的问题创建一个优化的网络研究搜索查询。

    Args:
        state: 包含用户问题的当前图状态
        config: 可运行程序的配置，包括 LLM 提供商设置

    Returns:
        包含状态更新的字典，其中包括包含生成查询的 search_query 键
    """
    configurable = Configuration.from_runnable_config(config)

    # 检查自定义的初始搜索查询数量
    if state.get("initial_search_query_count") is None:
        state["initial_search_query_count"] = configurable.number_of_initial_queries

    # 使用工厂初始化 LLM
    llm = LLMFactory.create_llm(
        provider=configurable.llm_provider,
        model_name=configurable.query_generator_model,
        temperature=1.0,
        max_retries=2,
    )
    structured_llm = llm.with_structured_output(SearchQueryList)

    # 格式化提示
    current_date = get_current_date()
    formatted_prompt = query_writer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        number_queries=state["initial_search_query_count"],
    )
    # 生成搜索查询
    try:
        print(f"调试：使用服务商 {configurable.llm_provider}，模型 {configurable.query_generator_model}")
        print(f"调试：格式化后的提示：{formatted_prompt[:200]}...")
        result = structured_llm.invoke(formatted_prompt)
        print(f"调试：LLM 结果：{result}")
        if result is None:
            print(f"警告：服务商 {configurable.llm_provider} 的 LLM 返回了 None")
            # Fallback to simple query generation
            return {"query_list": [get_research_topic(state["messages"])]}
        return {"query_list": result.query or []}
    except Exception as e:
        print(f"generate_query 出错：{e}")
        print(f"服务商：{configurable.llm_provider}，模型：{configurable.query_generator_model}")
        # Fallback to simple query generation
        return {"query_list": [get_research_topic(state["messages"])]}


def continue_to_web_research(state: QueryGenerationState):
    """LangGraph 节点，将搜索查询发送到网络研究节点。

    用于生成 n 个网络研究节点，每个搜索查询对应一个。
    """
    return [
        Send("web_research", {"search_query": search_query, "id": int(idx)})
        for idx, search_query in enumerate(state["query_list"])
    ]


def web_research(state: WebSearchState, config: RunnableConfig) -> OverallState:
    """LangGraph 节点，根据 LLM 提供商使用适当的搜索方法执行网络研究。

    根据配置的 LLM 提供商，使用本地 Gemini 谷歌搜索或外部搜索 API 执行网络搜索。

    Args:
        state: 包含搜索查询和研究循环次数的当前图状态
        config: 可运行程序的配置，包括搜索 API 设置

    Returns:
        包含状态更新的字典，包括 sources_gathered、research_loop_count 和 web_research_results
    """
    # Configure
    configurable = Configuration.from_runnable_config(config)
    formatted_prompt = web_searcher_instructions.format(
        current_date=get_current_date(),
        research_topic=state["search_query"],
    )

    # 使用 SearchUtils 处理不同的服务商
    return SearchUtils.perform_web_research(
        search_query=state["search_query"],
        provider=configurable.llm_provider,
        model_name=configurable.query_generator_model,
        prompt=formatted_prompt,
        search_id=state["id"],
        config=config
    )


def reflection(state: OverallState, config: RunnableConfig) -> ReflectionState:
    """LangGraph 节点，识别知识差距并生成潜在的后续查询。

    分析当前摘要以确定需要进一步研究的领域，并生成潜在的后续查询。
    使用结构化输出以 JSON 格式提取后续查询。

    Args:
        state: 包含运行中摘要和研究主题的当前图状态
        config: 可运行程序的配置，包括 LLM 提供商设置

    Returns:
        包含状态更新的字典，其中包括包含生成的后续查询的 search_query 键
    """
    configurable = Configuration.from_runnable_config(config)
    # 增加研究循环次数
    state["research_loop_count"] = state.get("research_loop_count", 0) + 1

    # 格式化提示
    current_date = get_current_date()
    formatted_prompt = reflection_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n\n---\n\n".join(state["web_research_result"]),
    )
    # 使用工厂初始化推理模型
    llm = LLMFactory.create_llm(
        provider=configurable.llm_provider,
        model_name=configurable.reflection_model,
        temperature=1.0,
        max_retries=2,
    )
    result = llm.with_structured_output(Reflection).invoke(formatted_prompt)

    return {
        "is_sufficient": result.is_sufficient,
        "knowledge_gap": result.knowledge_gap,
        "follow_up_queries": result.follow_up_queries or [],
        "research_loop_count": state["research_loop_count"],
        "number_of_ran_queries": len(state["search_query"]),
    }


def evaluate_research(
    state: ReflectionState,
    config: RunnableConfig,
) -> OverallState:
    """LangGraph 路由功能，确定研究流程的下一步。

    通过根据配置的最大研究循环次数决定是继续收集信息还是最终确定摘要来控制研究循环。

    Args:
        state: 包含研究循环次数的当前图状态
        config: 可运行程序的配置，包括 max_research_loops 设置

    Returns:
        指示下一个要访问的节点的字符串字面量（"web_research" 或 "finalize_summary"）
    """
    configurable = Configuration.from_runnable_config(config)
    max_research_loops = (
        state.get("max_research_loops")
        if state.get("max_research_loops") is not None
        else configurable.max_research_loops
    )
    if state["is_sufficient"] or state["research_loop_count"] >= max_research_loops:
        return "finalize_answer"
    else:
        return [
            Send(
                "web_research",
                {
                    "search_query": follow_up_query,
                    "id": state["number_of_ran_queries"] + int(idx),
                },
            )
            for idx, follow_up_query in enumerate(state["follow_up_queries"])
        ]


def finalize_answer(state: OverallState, config: RunnableConfig):
    """LangGraph 节点，最终确定研究摘要。

    通过去重和格式化来源准备最终输出，然后将它们与运行中摘要结合起来，
    创建一个带有适当引用的结构良好的研究报告。

    Args:
        state: 包含运行中摘要和收集来源的当前图状态

    Returns:
        包含状态更新的字典，其中包括包含格式化最终摘要和来源的 running_summary 键
    """
    configurable = Configuration.from_runnable_config(config)

    # 格式化提示
    current_date = get_current_date()
    formatted_prompt = answer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n---\n\n".join(state["web_research_result"]),
    )

    # 使用工厂初始化答案模型
    llm = LLMFactory.create_llm(
        provider=configurable.llm_provider,
        model_name=configurable.answer_model,
        temperature=0,
        max_retries=2,
    )
    result = llm.invoke(formatted_prompt)

    # 用原始 URL 替换短 URL，并将所有使用的 URL 添加到 sources_gathered
    unique_sources = []
    for source in state["sources_gathered"]:
        if source["short_url"] in result.content:
            result.content = result.content.replace(
                source["short_url"], source["value"]
            )
            unique_sources.append(source)

    return {
        "messages": [AIMessage(content=result.content)],
        "sources_gathered": unique_sources,
    }


# Create our Agent Graph
builder = StateGraph(OverallState, config_schema=Configuration)

# Define the nodes we will cycle between
builder.add_node("generate_query", generate_query)
builder.add_node("web_research", web_research)
builder.add_node("reflection", reflection)
builder.add_node("finalize_answer", finalize_answer)

# Set the entrypoint as `generate_query`
# This means that this node is the first one called
builder.add_edge(START, "generate_query")
# Add conditional edge to continue with search queries in a parallel branch
builder.add_conditional_edges(
    "generate_query", continue_to_web_research, ["web_research"]
)
# Reflect on the web research
builder.add_edge("web_research", "reflection")
# Evaluate the research
builder.add_conditional_edges(
    "reflection", evaluate_research, ["web_research", "finalize_answer"]
)
# Finalize the answer
builder.add_edge("finalize_answer", END)

graph = builder.compile(name="pro-search-agent")

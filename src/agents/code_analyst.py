"""
代码分析员 Agent

负责：
1. 从代码库中提取系统架构信息
2. 分析算法实现细节
3. 提取实验参数和配置
4. 为方法章节和实验章节提供素材
"""

from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate


CODE_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一个专业的代码分析员。
根据提供的代码检索结果，提取关键的技术信息。

**重要约束**：
1. 只能基于提供的代码检索结果进行描述
2. 严禁编造代码中不存在的功能
3. 如果检索结果中没有相关信息，请明确说明
4. 提取的信息应包括：系统架构、核心算法、实现细节、实验参数"""),
    ("human", """研究主题：{topic}

代码检索结果：
{code_context}

请提取以下信息：
1. 系统整体架构和模块组成
2. 核心算法和模型设计
3. 实验参数和训练配置
4. 关键实现细节

只提取代码中实际存在的信息：""")
])


def analyze_code(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    代码分析员：从代码库提取技术信息

    Args:
        state: 当前状态

    Returns:
        更新后的状态，包含 code_analysis
    """
    topic = state.get("topic", "")
    llm = state.get("llm", None)
    code_retriever = state.get("code_retriever", None)

    code_results = []
    if code_retriever:
        queries = [
            f"{topic} 系统架构",
            f"{topic} 模型定义",
            f"{topic} 训练流程",
            f"{topic} 实验配置",
            f"{topic} 数据处理"
        ]
        for query in queries:
            results = code_retriever.query(query, top_k=3)
            code_results.extend([r['text'] for r in results])

    code_context = "\n\n".join(code_results[:8]) if code_results else "未找到相关代码"

    prompt = CODE_ANALYSIS_PROMPT.format(topic=topic, code_context=code_context)

    if llm:
        response = llm.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
    else:
        content = "代码分析结果。（需要 LLM 生成）"

    state["code_analysis"] = content
    print("完成代码分析")
    return state

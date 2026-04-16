"""
事实核查 Agent

负责：
1. 验证章节内容中关于代码的描述是否与实际代码一致
2. 检查方法描述是否与代码实现匹配
3. 检查实验参数是否与代码配置一致
"""

import re
from typing import Dict, Any, List, Set
from langchain_core.prompts import ChatPromptTemplate


FACT_CHECK_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一个严格的事实核查员。
你需要验证论文草稿中关于代码和系统的描述是否与实际代码一致。

**核查要点**：
1. 提到的模型架构是否在代码中存在
2. 描述的算法流程是否与代码实现匹配
3. 实验参数（如学习率、batch size）是否与代码配置一致
4. 系统功能描述是否与代码实现匹配
5. 数据处理流程是否与代码一致

如果发现不一致，请列出具体的问题。"""),
    ("human", """章节名称：{section_name}
章节草稿：
{draft_content}

代码检索结果：
{code_context}

请核查草稿中关于代码的描述是否准确，列出所有不一致之处：""")
])


def fact_check(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    事实核查：验证章节内容与代码的一致性

    Args:
        state: 当前状态

    Returns:
        更新后的状态，包含 fact_check_errors
    """
    drafts = state.get("drafts", {})
    code_retriever = state.get("code_retriever", None)
    llm = state.get("llm", None)
    errors = state.get("errors", [])

    code_sections = [
        "2 柑橘多视角图像采集与数据处理",
        "3 基于多视角注意力融合的检测模型构建",
        "4 实验结果与对比分析",
        "5 柑橘实蝇智能检测与问答系统设计与实现"
    ]

    fact_check_errors = []

    for section_name in code_sections:
        draft_content = drafts.get(section_name, "")
        if not draft_content:
            continue

        code_results = []
        if code_retriever:
            results = code_retriever.query(f"{section_name} 实现", top_k=5)
            code_results.extend([r['text'] for r in results])

        code_context = "\n\n".join(code_results[:5]) if code_results else "未找到相关代码"

        if llm and code_context != "未找到相关代码":
            prompt = FACT_CHECK_PROMPT.format(
                section_name=section_name,
                draft_content=draft_content[:2000],
                code_context=code_context[:2000]
            )
            response = llm.invoke(prompt)
            check_result = response.content if hasattr(response, 'content') else str(response)

            if any(kw in check_result for kw in ["不一致", "错误", "不存在", "不匹配", "不符"]):
                fact_check_errors.append(f"事实核查 - {section_name}: {check_result}")
                errors.append(f"事实核查失败 - {section_name}")

    state["fact_check_errors"] = fact_check_errors
    state["errors"] = errors

    if fact_check_errors:
        print(f"事实核查发现 {len(fact_check_errors)} 个问题")
    else:
        print("事实核查通过")

    return state

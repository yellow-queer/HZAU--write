"""
文献研究员 Agent

负责：
1. 从文献库中提取关键信息
2. 总结研究现状和趋势
3. 为章节主笔提供文献素材
"""

from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate


LITERATURE_REVIEW_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一个专业的文献研究员。
根据提供的文献检索结果，整理出研究现状综述。

**强制约束**：
1. 必须且只能使用提供的 EndNote Citation Keys 进行引用
2. 引用格式必须为 \\cite{{key}}
3. 严禁编造不在 citation_keys 列表中的引文
4. 按研究主题分类组织文献
5. 提取每篇文献的核心贡献和方法

可用 Citation Keys: {citation_keys}"""),
    ("human", """研究主题：{topic}

文献检索结果：
{literature_context}

可用 Citation Keys: {citation_keys}

请整理文献综述素材，包括：
1. 各研究方向的主要文献和贡献
2. 研究趋势和发展脉络
3. 当前研究的不足和空白

使用 \\cite{{key}} 格式引用：""")
])


def review_literature(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    文献研究员：从文献库提取关键信息

    Args:
        state: 当前状态

    Returns:
        更新后的状态，包含 literature_summary
    """
    topic = state.get("topic", "")
    citation_keys = state.get("citation_keys", [])
    llm = state.get("llm", None)
    literature_retriever = state.get("literature_retriever", None)

    literature_results = []
    if literature_retriever:
        queries = [
            f"{topic} 研究现状",
            f"{topic} 综述",
            f"{topic} 最新进展",
            f"{topic} 技术方法"
        ]
        for query in queries:
            results = literature_retriever.query(query, top_k=3)
            literature_results.extend([r['text'] for r in results])

    literature_context = "\n\n".join(literature_results[:8]) if literature_results else "未找到相关文献"
    citation_keys_str = ", ".join(citation_keys)

    prompt = LITERATURE_REVIEW_PROMPT.format(
        topic=topic,
        literature_context=literature_context,
        citation_keys=citation_keys_str
    )

    if llm:
        response = llm.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
    else:
        content = f"文献综述素材。（需要 LLM 生成，引用：{citation_keys_str}）"

    state["literature_summary"] = content
    print("完成文献研究")
    return state

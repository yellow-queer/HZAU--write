from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END

from src.agents.state import PaperDraftState
from src.agents.planner import generate_outline
from src.agents.writers import (
    write_chapter1,
    write_chapter2,
    write_chapter3,
    write_chapter4,
    write_chapter5,
    write_chapter6
)
from src.agents.reviewer import check_citations


def init_state(state: Dict[str, Any]) -> Dict[str, Any]:
    print("初始化工作流状态...")
    citation_keys = state.get("citation_keys", [])
    print(f"已加载 {len(citation_keys)} 个 Citation Keys")
    return state


def fact_check(state: Dict[str, Any]) -> Dict[str, Any]:
    drafts = state.get("drafts", {})
    errors = state.get("errors", [])
    code_retriever = state.get("code_retriever")
    literature_retriever = state.get("literature_retriever")

    code_chapters = [
        "2 柑橘多视角图像采集与数据处理",
        "3 基于多视角注意力融合的检测模型构建",
        "4 实验结果与对比分析",
        "5 柑橘实蝇智能检测与问答系统设计与实现"
    ]

    for chapter_name in code_chapters:
        content = drafts.get(chapter_name, "")
        if not content:
            continue
        if code_retriever:
            try:
                results = code_retriever.query(f"{chapter_name} 核心实现", top_k=1)
                if not results:
                    error_msg = f"章节 '{chapter_name}' 的内容可能缺乏代码支撑，请核实"
                    errors.append(error_msg)
            except Exception:
                pass

    lit_chapters = ["1 绪论"]
    citation_keys = set(state.get("citation_keys", []))
    import re
    for chapter_name in lit_chapters:
        content = drafts.get(chapter_name, "")
        if not content:
            continue
        cite_pattern = r'\\cite\{([^}]+)\}'
        citations = re.findall(cite_pattern, content)
        if not citations and citation_keys:
            error_msg = f"章节 '{chapter_name}' 缺少文献引用，绪论章节必须包含引用"
            errors.append(error_msg)

    state["errors"] = errors
    if errors:
        print(f"事实检查发现 {len(errors)} 个问题")
        state["sections_to_rewrite"] = list(set(
            state.get("sections_to_rewrite", []) +
            [e.split("'")[1] for e in errors if "'" in e]
        ))
    else:
        print("事实检查通过")
        state["sections_to_rewrite"] = []

    return state


def should_rewrite(state: Dict[str, Any]) -> Literal["rewrite", "continue"]:
    errors = state.get("errors", [])
    sections_to_rewrite = state.get("sections_to_rewrite", [])
    max_retries = state.get("max_retries", 3)
    retries = state.get("retries", 0)

    if sections_to_rewrite and retries < max_retries:
        state["retries"] = retries + 1
        return "rewrite"
    elif sections_to_rewrite and retries >= max_retries:
        print(f"达到最大重试次数 {max_retries}，继续执行")
        state["errors"] = []
        state["sections_to_rewrite"] = []
        return "continue"
    else:
        return "continue"


def route_to_writer(state: Dict[str, Any]) -> str:
    sections_to_rewrite = state.get("sections_to_rewrite", [])

    if not sections_to_rewrite:
        return "review_citations"

    section = sections_to_rewrite[0]

    if "绪论" in section:
        return "write_chapter1"
    elif "图像采集" in section or "数据处理" in section:
        return "write_chapter2"
    elif "模型构建" in section or "注意力融合" in section:
        return "write_chapter3"
    elif "实验" in section or "对比分析" in section:
        return "write_chapter4"
    elif "系统" in section or "问答" in section:
        return "write_chapter5"
    elif "总结" in section or "展望" in section:
        return "write_chapter6"
    else:
        return "review_citations"


def create_workflow():
    workflow = StateGraph(PaperDraftState)

    workflow.add_node("init", init_state)
    workflow.add_node("plan_outline", generate_outline)
    workflow.add_node("write_chapter1", write_chapter1)
    workflow.add_node("write_chapter2", write_chapter2)
    workflow.add_node("write_chapter3", write_chapter3)
    workflow.add_node("write_chapter4", write_chapter4)
    workflow.add_node("write_chapter5", write_chapter5)
    workflow.add_node("write_chapter6", write_chapter6)
    workflow.add_node("fact_check", fact_check)
    workflow.add_node("review_citations", check_citations)

    workflow.set_entry_point("init")

    workflow.add_edge("init", "plan_outline")
    workflow.add_edge("plan_outline", "write_chapter1")
    workflow.add_edge("write_chapter1", "write_chapter2")
    workflow.add_edge("write_chapter2", "write_chapter3")
    workflow.add_edge("write_chapter3", "write_chapter4")
    workflow.add_edge("write_chapter4", "write_chapter5")
    workflow.add_edge("write_chapter5", "write_chapter6")
    workflow.add_edge("write_chapter6", "fact_check")
    workflow.add_edge("fact_check", "review_citations")

    workflow.add_conditional_edges(
        "review_citations",
        should_rewrite,
        {
            "rewrite": route_to_writer,
            "continue": END
        }
    )

    app = workflow.compile()
    return app

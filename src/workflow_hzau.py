from typing import Dict, Any, Literal, List
from langgraph.graph import StateGraph, END

from src.agents.state import PaperDraftState
from src.agents.planner import generate_outline, DEFAULT_CHAPTER_NAMES
from src.agents.writers import (
    write_chapter1,
    write_chapter2,
    write_chapter3,
    write_chapter4,
    write_chapter5,
    write_chapter6
)
from src.agents.reviewer import check_citations
from src.agents.output_writer import write_chapter_to_file, init_output_file


DEFAULT_CODE_CHAPTER_KEYS = [
    "write_chapter2",
    "write_chapter3",
    "write_chapter4",
    "write_chapter5"
]


def get_chapter_names(state: Dict[str, Any]) -> Dict[str, str]:
    research_context = state.get("research_context", {})
    chapters = research_context.get("chapters", {})
    if chapters:
        return chapters
    return DEFAULT_CHAPTER_NAMES


def get_code_chapters(state: Dict[str, Any]) -> List[str]:
    research_context = state.get("research_context", {})
    code_chapter_keys = research_context.get("code_chapter_keys", DEFAULT_CODE_CHAPTER_KEYS)
    chapter_names = get_chapter_names(state)
    return [chapter_names.get(key, key) for key in code_chapter_keys]


def init_state(state: Dict[str, Any]) -> Dict[str, Any]:
    print("初始化工作流状态...")
    citation_keys = state.get("citation_keys", [])
    print(f"已加载 {len(citation_keys)} 个 Citation Keys")

    output_file = state.get("output_file")
    topic = state.get("topic", "未命名论文")

    if output_file:
        try:
            if init_output_file(output_file, topic):
                print(f"✓ 已初始化输出文件：{output_file}")
            else:
                print(f"⚠ 输出文件初始化失败，将跳过增量写入")
        except Exception as e:
            print(f"⚠ 初始化输出文件时出错：{e}")
    else:
        print("⚠ 未指定输出文件路径，将跳过增量写入")

    return state


def wrap_chapter_writer(writer_func: callable, chapter_key: str):
    def wrapped_writer(state: Dict[str, Any]) -> Dict[str, Any]:
        chapter_names = get_chapter_names(state)
        chapter_name = chapter_names.get(chapter_key, chapter_key)

        try:
            print(f"\n{'=' * 60}")
            print(f"开始撰写章节: {chapter_name}")
            print(f"{'=' * 60}")

            new_state = writer_func(state)

            output_file = new_state.get("output_file")
            drafts = new_state.get("drafts", {})
            content = drafts.get(chapter_name, "")

            if output_file and content:
                try:
                    if write_chapter_to_file(output_file, chapter_name, content):
                        print(f"✓ 已写入章节：{chapter_name}")
                    else:
                        print(f"⚠ 章节写入失败：{chapter_name}")
                except Exception as e:
                    print(f"⚠ 写入章节时出错 ({chapter_name})：{e}")
            elif not output_file:
                pass
            elif not content:
                print(f"⚠ 章节 {chapter_name} 内容为空，跳过写入")

            return new_state

        except Exception as e:
            print(f"\n{'!' * 60}")
            print(f"❌ 章节 '{chapter_name}' 撰写失败")
            print(f"{'!' * 60}")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误信息: {str(e)}")

            import traceback
            print(f"\n详细错误堆栈:")
            traceback.print_exc()

            print(f"\n⚠️ 检测到问题，建议：")
            print(f"  1. 检查输出文件中的已完成章节")
            print(f"  2. 修复问题后重新运行")
            print(f"  3. 系统将从中断处继续")

            completed_chapters = []
            drafts = state.get("drafts", {})
            for name, draft_content in drafts.items():
                if draft_content:
                    completed_chapters.append(name)

            if completed_chapters:
                print(f"\n已完成的章节:")
                for ch in completed_chapters:
                    print(f"  ✓ {ch}")

            error_entry = {
                "chapter": chapter_name,
                "error_type": type(e).__name__,
                "error_message": str(e)
            }
            state["chapter_errors"] = state.get("chapter_errors", []) + [error_entry]

            return state

    return wrapped_writer


write_chapter1_with_save = wrap_chapter_writer(write_chapter1, "write_chapter1")
write_chapter2_with_save = wrap_chapter_writer(write_chapter2, "write_chapter2")
write_chapter3_with_save = wrap_chapter_writer(write_chapter3, "write_chapter3")
write_chapter4_with_save = wrap_chapter_writer(write_chapter4, "write_chapter4")
write_chapter5_with_save = wrap_chapter_writer(write_chapter5, "write_chapter5")
write_chapter6_with_save = wrap_chapter_writer(write_chapter6, "write_chapter6")


def fact_check(state: Dict[str, Any]) -> Dict[str, Any]:
    drafts = state.get("drafts", {})
    errors = state.get("errors", [])
    code_retriever = state.get("code_retriever")
    literature_retriever = state.get("literature_retriever")

    code_chapters = get_code_chapters(state)

    if code_retriever is None:
        print("⚠ code_retriever 为 None，跳过代码相关章节的事实检查")
    else:
        for chapter_name in code_chapters:
            content = drafts.get(chapter_name, "")
            if not content:
                continue
            try:
                results = code_retriever.query(f"{chapter_name} 核心实现", top_k=1)
                if not results:
                    error_msg = f"章节 '{chapter_name}' 的内容可能缺乏代码支撑，请核实"
                    errors.append(error_msg)
            except Exception as e:
                print(f"⚠ 代码检索失败 '{chapter_name}': {e}")

    chapter_names = get_chapter_names(state)
    lit_chapter_name = chapter_names.get("write_chapter1", "1 绪论")
    lit_chapters = [lit_chapter_name]
    citation_keys = set(state.get("citation_keys", []))
    import re
    for chapter_name in lit_chapters:
        content = drafts.get(chapter_name, "")
        if not content:
            continue
        cite_pattern = r'\\cite\{([^}]+)\}'
        citations = re.findall(cite_pattern, content)
        if not citations and citation_keys:
            error_msg = f"章节 '{chapter_name}' 缺少文献引用，{lit_chapter_name}必须包含引用"
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
    chapter_names = get_chapter_names(state)
    
    chapter1_name = chapter_names.get("write_chapter1", "1 绪论")
    chapter2_name = chapter_names.get("write_chapter2", "2 研究方法与数据")
    chapter3_name = chapter_names.get("write_chapter3", "3 模型设计与实现")
    chapter4_name = chapter_names.get("write_chapter4", "4 实验结果与分析")
    chapter5_name = chapter_names.get("write_chapter5", "5 系统开发与应用")
    chapter6_name = chapter_names.get("write_chapter6", "6 总结与展望")

    if chapter1_name in section:
        return "write_chapter1"
    elif chapter2_name in section:
        return "write_chapter2"
    elif chapter3_name in section:
        return "write_chapter3"
    elif chapter4_name in section:
        return "write_chapter4"
    elif chapter5_name in section:
        return "write_chapter5"
    elif chapter6_name in section:
        return "write_chapter6"
    else:
        chapter_keywords = {
            "write_chapter1": ["绪论", "引言", "背景"],
            "write_chapter2": ["方法", "数据", "研究设计"],
            "write_chapter3": ["模型", "设计", "架构", "算法"],
            "write_chapter4": ["实验", "结果", "分析", "对比"],
            "write_chapter5": ["系统", "应用", "实现", "部署"],
            "write_chapter6": ["总结", "展望", "结论", "未来"]
        }
        
        for chapter_key, keywords in chapter_keywords.items():
            for keyword in keywords:
                if keyword in section:
                    return chapter_key
        
        return "review_citations"


def create_workflow():
    workflow = StateGraph(PaperDraftState)

    workflow.add_node("init", init_state)
    workflow.add_node("plan_outline", generate_outline)
    workflow.add_node("write_chapter1", write_chapter1_with_save)
    workflow.add_node("write_chapter2", write_chapter2_with_save)
    workflow.add_node("write_chapter3", write_chapter3_with_save)
    workflow.add_node("write_chapter4", write_chapter4_with_save)
    workflow.add_node("write_chapter5", write_chapter5_with_save)
    workflow.add_node("write_chapter6", write_chapter6_with_save)
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

    def rewrite_router(state: Dict[str, Any]) -> str:
        rewrite_decision = should_rewrite(state)
        if rewrite_decision == "continue":
            return "continue"
        return route_to_writer(state)

    workflow.add_conditional_edges(
        "review_citations",
        rewrite_router,
        {
            "continue": END,
            "write_chapter1": "write_chapter1",
            "write_chapter2": "write_chapter2",
            "write_chapter3": "write_chapter3",
            "write_chapter4": "write_chapter4",
            "write_chapter5": "write_chapter5",
            "write_chapter6": "write_chapter6",
            "review_citations": "review_citations"
        }
    )

    app = workflow.compile()
    return app

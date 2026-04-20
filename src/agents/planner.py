import json
import re
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate


OUTLINE_SYSTEM_BASE = """你是一个专业的学术论文写作助手。
根据用户提供的研究主题和科研工作内容，生成一个符合学术论文要求的大纲。

要求：
1. 大纲必须包含以下章节结构：
{chapters_structure}

2. 每个章节提供简短的描述，说明该章节应该包含的内容

3. 使用 JSON 格式返回大纲，格式如下：
{{
  "章节名称 1": "章节描述",
  "章节名称 2": "章节描述"
}}

只返回 JSON 格式的大纲，不要包含其他内容。"""

OUTLINE_CONTEXT_INSTRUCTION = """
**用户提供的科研工作内容（必须据此调整大纲描述）**：
{research_context_hint}

**重要**：请根据上述用户科研内容调整大纲中每个章节的描述，确保大纲准确反映用户的实际研究工作。
特别是创新点、实验结果、系统架构等关键信息必须在大纲中体现。"""


def _format_research_context_for_outline(context: Dict[str, Any]) -> str:
    if not context:
        return ""

    parts = []

    if context.get("title"):
        parts.append(f"【论文标题】{context['title']}")
    if context.get("research_summary"):
        parts.append(f"【研究概述】{context['research_summary']}")
    if context.get("innovations"):
        innovations = "\n".join(f"  - {i}" for i in context["innovations"])
        parts.append(f"【核心创新点】\n{innovations}")

    method = context.get("methodology", {})
    if method.get("data_collection"):
        parts.append(f"【数据采集】{method['data_collection']}")
    if method.get("model_architecture"):
        parts.append(f"【模型架构】{method['model_architecture']}")
    if method.get("comparison_models"):
        models = ", ".join(m["name"] for m in method["comparison_models"])
        parts.append(f"【对比模型】{models}")
    if method.get("training_strategy"):
        parts.append(f"【训练策略】{method['training_strategy']}")

    exp = context.get("experiment_results", {})
    if exp.get("key_metrics"):
        metrics = ", ".join(
            f"{m['metric']}={m['our_method']}" for m in exp["key_metrics"]
        )
        parts.append(f"【关键指标】{metrics}")
    if exp.get("key_findings"):
        findings = "\n".join(f"  - {f}" for f in exp["key_findings"])
        parts.append(f"【关键发现】\n{findings}")

    sys_impl = context.get("system_implementation", {})
    if sys_impl.get("architecture"):
        parts.append(f"【系统架构】{sys_impl['architecture']}")

    lim = context.get("limitations_and_future", {})
    if lim.get("limitations"):
        limitations = ", ".join(lim["limitations"])
        parts.append(f"【研究不足】{limitations}")
    if lim.get("future_work"):
        future = ", ".join(lim["future_work"])
        parts.append(f"【未来展望】{future}")

    if context.get("additional_notes"):
        parts.append(f"【补充说明】{context['additional_notes']}")

    return "\n\n".join(parts)


DEFAULT_CHAPTER_NAMES = {
    "write_chapter1": "1 绪论",
    "write_chapter2": "2 研究方法与数据",
    "write_chapter3": "3 模型设计与实现",
    "write_chapter4": "4 实验结果与分析",
    "write_chapter5": "5 系统开发与应用",
    "write_chapter6": "6 总结与展望"
}


DEFAULT_OUTLINE = {
    "1 绪论": "论述研究背景与意义、国内外研究现状、研究内容与创新点",
    "2 研究方法与数据": "介绍研究方法与数据来源、数据采集与预处理流程、实验设计与设置",
    "3 模型设计与实现": "详细阐述模型架构设计、核心算法实现、技术路线与创新方法",
    "4 实验结果与分析": "呈现实验结果、对比分析、性能评估与讨论",
    "5 系统开发与应用": "介绍系统设计与实现、功能模块、应用场景与部署方案",
    "6 总结与展望": "总结全文工作、指出研究不足、提出未来展望"
}


def generate_outline(state: Dict[str, Any], llm=None) -> Dict[str, Any]:
    topic = state.get("topic", "")
    research_context = state.get("research_context", {})
    
    chapters = research_context.get("chapters", DEFAULT_CHAPTER_NAMES)
    chapter_names = list(chapters.values())
    
    chapters_structure = "\n".join(f"   - {name}" for name in chapter_names)

    if not topic:
        state["errors"].append("错误：研究主题为空")
        return state

    research_context_hint = _format_research_context_for_outline(research_context)

    if research_context_hint:
        system_content = OUTLINE_SYSTEM_BASE.format(chapters_structure=chapters_structure) + OUTLINE_CONTEXT_INSTRUCTION.format(
            research_context_hint=research_context_hint
        )
    else:
        system_content = OUTLINE_SYSTEM_BASE.format(chapters_structure=chapters_structure)

    focus = state.get("focus", "")
    if focus:
        system_content += f"\n\n**写作重心**：{focus}\n请根据上述写作重心调整大纲中各章节的描述，使重点章节的描述更加详细。"

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_content),
        ("human", "研究主题：{topic}")
    ]).format(topic=topic)

    if llm:
        response = llm.invoke(prompt)
        outline_text = response.content if hasattr(response, 'content') else str(response)
    else:
        outline = {}
        for key, name in chapters.items():
            if name in DEFAULT_OUTLINE:
                outline[name] = DEFAULT_OUTLINE[name]
            else:
                outline[name] = f"论述{name}的核心内容"
        state["outline"] = outline
        if research_context:
            _enrich_outline_with_context(state["outline"], research_context)
        print(f"生成论文大纲（默认）：{list(state['outline'].keys())}")
        return state

    json_match = re.search(r'\{.*\}', outline_text, re.DOTALL)
    if json_match:
        try:
            outline = json.loads(json_match.group())
            state["outline"] = outline
            print(f"生成论文大纲：{list(outline.keys())}")
        except json.JSONDecodeError:
            outline = {}
            for key, name in chapters.items():
                if name in DEFAULT_OUTLINE:
                    outline[name] = DEFAULT_OUTLINE[name]
                else:
                    outline[name] = f"论述{name}的核心内容"
            state["outline"] = outline
            if research_context:
                _enrich_outline_with_context(state["outline"], research_context)
            state["errors"].append("警告：大纲解析失败，使用默认大纲")
    else:
        outline = {}
        for key, name in chapters.items():
            if name in DEFAULT_OUTLINE:
                outline[name] = DEFAULT_OUTLINE[name]
            else:
                outline[name] = f"论述{name}的核心内容"
        state["outline"] = outline
        if research_context:
            _enrich_outline_with_context(state["outline"], research_context)

    return state


def _enrich_outline_with_context(outline: Dict[str, str], context: Dict[str, Any]) -> Dict[str, str]:
    chapter1_name = context.get("chapters", {}).get("write_chapter1", "1 绪论")
    chapter2_name = context.get("chapters", {}).get("write_chapter2", "2 研究方法与数据")
    chapter3_name = context.get("chapters", {}).get("write_chapter3", "3 模型设计与实现")
    chapter4_name = context.get("chapters", {}).get("write_chapter4", "4 实验结果与分析")
    chapter5_name = context.get("chapters", {}).get("write_chapter5", "5 系统开发与应用")
    chapter6_name = context.get("chapters", {}).get("write_chapter6", "6 总结与展望")
    
    if context.get("innovations"):
        innovations = ".".join(context["innovations"])
        if chapter1_name in outline:
            outline[chapter1_name] += f"。创新点：{innovations}"

    method = context.get("methodology", {})
    if method.get("data_collection") and chapter2_name in outline:
        outline[chapter2_name] += f"。采集方案：{method['data_collection'][:100]}"

    if method.get("model_architecture") and chapter3_name in outline:
        outline[chapter3_name] += f"。模型：{method['model_architecture'][:100]}"

    exp = context.get("experiment_results", {})
    if exp.get("key_metrics") and chapter4_name in outline:
        metrics = ", ".join(
            f"{m['metric']}={m['our_method']}" for m in exp["key_metrics"]
        )
        outline[chapter4_name] += f"。关键指标：{metrics}"

    lim = context.get("limitations_and_future", {})
    if lim.get("future_work") and chapter6_name in outline:
        future = ".".join(lim["future_work"])
        outline[chapter6_name] += f"。展望：{future}"

    return outline

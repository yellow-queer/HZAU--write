import json
import re
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate


OUTLINE_SYSTEM_BASE = """你是一个专业的学术论文写作助手。
根据用户提供的研究主题和科研工作内容，生成一个符合华中农业大学本科毕业论文要求的大纲。

要求：
1. 大纲必须包含以下 6 章结构：
   - 1 绪论（含研究背景与意义、国内外研究现状、研究内容与创新点）
   - 2 柑橘多视角图像采集与数据处理（含多视角图像采集方案、数据预处理与数据集构建）
   - 3 基于多视角注意力融合的检测模型构建（含多视角注意力融合网络设计、对比基线模型构建、模型训练与优化策略）
   - 4 实验结果与对比分析（含实验环境与评估指标、多模型性能对比分析、特征可视化与机理分析）
   - 5 柑橘实蝇智能检测与问答系统设计与实现（含系统总体架构与交互设计、图像质量评估与智能检测模块、基于大模型与 RAG 的智能问答模块、系统部署与公网访问）
   - 6 总结与展望（含全文总结、研究不足与未来展望）

2. 每个章节提供简短的描述，说明该章节应该包含的内容

3. 使用 JSON 格式返回大纲，格式如下：
{
  "1 绪论": "章节描述",
  "2 柑橘多视角图像采集与数据处理": "章节描述",
  "3 基于多视角注意力融合的检测模型构建": "章节描述",
  "4 实验结果与对比分析": "章节描述",
  "5 柑橘实蝇智能检测与问答系统设计与实现": "章节描述",
  "6 总结与展望": "章节描述"
}

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


DEFAULT_OUTLINE = {
    "1 绪论": "论述柑橘实蝇危害、传统破坏性检测的痛点，以及低成本无损检测的产业需求",
    "2 柑橘多视角图像采集与数据处理": "介绍基于旋转平台与双摄像头的采集装置，以及全覆盖拍摄流程",
    "3 基于多视角注意力融合的检测模型构建": "核心算法章：详细阐述以 ConvNeXt 为骨干网络的特征融合与分类过程",
    "4 实验结果与对比分析": "对比 5 种模型在测试集上的表现，分析注意力融合模型的优势",
    "5 柑橘实蝇智能检测与问答系统设计与实现": "介绍基于 Flask 的后端架构和毛玻璃风格 UI 设计",
    "6 总结与展望": "回顾从算法设计、对比实验到系统全栈开发的完整研究闭环"
}


def generate_outline(state: Dict[str, Any], llm=None) -> Dict[str, Any]:
    topic = state.get("topic", "")
    research_context = state.get("research_context", {})

    if not topic:
        state["errors"].append("错误：研究主题为空")
        return state

    research_context_hint = _format_research_context_for_outline(research_context)

    if research_context_hint:
        system_content = OUTLINE_SYSTEM_BASE + OUTLINE_CONTEXT_INSTRUCTION.format(
            research_context_hint=research_context_hint
        )
    else:
        system_content = OUTLINE_SYSTEM_BASE

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_content),
        ("human", "研究主题：{topic}")
    ]).format(topic=topic)

    if llm:
        response = llm.invoke(prompt)
        outline_text = response.content if hasattr(response, 'content') else str(response)
    else:
        state["outline"] = DEFAULT_OUTLINE.copy()
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
            state["outline"] = DEFAULT_OUTLINE.copy()
            if research_context:
                _enrich_outline_with_context(state["outline"], research_context)
            state["errors"].append("警告：大纲解析失败，使用华中农业大学毕业论文大纲")
    else:
        state["outline"] = DEFAULT_OUTLINE.copy()
        if research_context:
            _enrich_outline_with_context(state["outline"], research_context)

    return state


def _enrich_outline_with_context(outline: Dict[str, str], context: Dict[str, Any]) -> Dict[str, str]:
    if context.get("innovations"):
        innovations = "；".join(context["innovations"])
        if "1 绪论" in outline:
            outline["1 绪论"] += f"。创新点：{innovations}"

    method = context.get("methodology", {})
    if method.get("data_collection") and "2 柑橘多视角图像采集与数据处理" in outline:
        outline["2 柑橘多视角图像采集与数据处理"] += f"。采集方案：{method['data_collection'][:100]}"

    if method.get("model_architecture") and "3 基于多视角注意力融合的检测模型构建" in outline:
        outline["3 基于多视角注意力融合的检测模型构建"] += f"。模型：{method['model_architecture'][:100]}"

    exp = context.get("experiment_results", {})
    if exp.get("key_metrics") and "4 实验结果与对比分析" in outline:
        metrics = ", ".join(
            f"{m['metric']}={m['our_method']}" for m in exp["key_metrics"]
        )
        outline["4 实验结果与对比分析"] += f"。关键指标：{metrics}"

    lim = context.get("limitations_and_future", {})
    if lim.get("future_work") and "6 总结与展望" in outline:
        future = "；".join(lim["future_work"])
        outline["6 总结与展望"] += f"。展望：{future}"

    return outline

import json
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate


RESEARCH_CONTEXT_INSTRUCTION = """
**用户提供的科研工作内容（必须优先参考）**：
{research_context_hint}

**重要**：上述用户科研内容是真实的研究成果，请务必在写作中充分体现这些内容。
如果检索结果与用户科研内容不一致，以用户科研内容为准。
"""


def _format_research_context(context: Dict[str, Any], chapter: str) -> str:
    if not context:
        return "（用户未提供科研工作内容，请基于检索结果和专业知识撰写）"

    parts = []

    if chapter == "1":
        if context.get("research_summary"):
            parts.append(f"【研究概述】{context['research_summary']}")
        if context.get("innovations"):
            innovations = "\n".join(f"  - {i}" for i in context["innovations"])
            parts.append(f"【核心创新点】\n{innovations}")
        method = context.get("methodology", {})
        if method.get("data_collection"):
            parts.append(f"【数据采集方案】{method['data_collection']}")
        if method.get("model_architecture"):
            parts.append(f"【核心模型】{method['model_architecture']}")

    elif chapter == "2":
        method = context.get("methodology", {})
        if method.get("data_collection"):
            parts.append(f"【数据采集方案】{method['data_collection']}")
        if context.get("research_summary"):
            parts.append(f"【研究概述】{context['research_summary']}")

    elif chapter == "3":
        method = context.get("methodology", {})
        if method.get("model_architecture"):
            parts.append(f"【核心模型架构】{method['model_architecture']}")
        if method.get("comparison_models"):
            models = "\n".join(
                f"  - {m['name']}：{m['description']}"
                for m in method["comparison_models"]
            )
            parts.append(f"【对比模型】\n{models}")
        if method.get("training_strategy"):
            parts.append(f"【训练策略】{method['training_strategy']}")
        if context.get("innovations"):
            innovations = "\n".join(f"  - {i}" for i in context["innovations"])
            parts.append(f"【核心创新点】\n{innovations}")

    elif chapter == "4":
        exp = context.get("experiment_results", {})
        if exp.get("environment"):
            parts.append(f"【实验环境】{exp['environment']}")
        if exp.get("key_metrics"):
            metrics = "\n".join(
                f"  - {m['metric']}：本方法 {m['our_method']}，最佳基线 {m['best_baseline']}"
                for m in exp["key_metrics"]
            )
            parts.append(f"【关键指标】\n{metrics}")
        if exp.get("key_findings"):
            findings = "\n".join(f"  - {f}" for f in exp["key_findings"])
            parts.append(f"【关键发现】\n{findings}")
        method = context.get("methodology", {})
        if method.get("comparison_models"):
            models = ", ".join(m["name"] for m in method["comparison_models"])
            parts.append(f"【对比模型列表】{models}")

    elif chapter == "5":
        sys_impl = context.get("system_implementation", {})
        if sys_impl.get("architecture"):
            parts.append(f"【系统架构】{sys_impl['architecture']}")
        if sys_impl.get("core_features"):
            features = "\n".join(f"  - {f}" for f in sys_impl["core_features"])
            parts.append(f"【核心功能】\n{features}")

    elif chapter == "6":
        if context.get("research_summary"):
            parts.append(f"【研究概述】{context['research_summary']}")
        if context.get("innovations"):
            innovations = "\n".join(f"  - {i}" for i in context["innovations"])
            parts.append(f"【核心创新点】\n{innovations}")
        lim = context.get("limitations_and_future", {})
        if lim.get("limitations"):
            limitations = "\n".join(f"  - {l}" for l in lim["limitations"])
            parts.append(f"【研究不足】\n{limitations}")
        if lim.get("future_work"):
            future = "\n".join(f"  - {f}" for f in lim["future_work"])
            parts.append(f"【未来展望】\n{future}")
        exp = context.get("experiment_results", {})
        if exp.get("key_metrics"):
            metrics = ", ".join(
                f"{m['metric']}={m['our_method']}" for m in exp["key_metrics"]
            )
            parts.append(f"【关键结果摘要】{metrics}")

    if context.get("additional_notes"):
        parts.append(f"【用户补充说明】{context['additional_notes']}")

    return "\n\n".join(parts) if parts else "（用户未提供该章节相关的科研内容，请基于检索结果撰写）"


CHAPTER1_SYSTEM = """你是一个专业的中文学术论文写作助手。
根据提供的文献检索结果和用户科研工作内容，撰写论文的"1 绪论"章节。

**章节内容指引**：
1.1 研究背景与意义：论述柑橘实蝇对柑橘产业的危害、传统破坏性检测方法（如剖果法）的痛点，以及低成本无损检测的产业需求
1.2 国内外研究现状：
  - 农产品无损检测技术发展（近红外光谱、机器视觉、高光谱成像等）
  - 深度学习在病虫害检测中的应用（CNN、目标检测、图像分类等）
  - 多视角图像融合技术的发展（视角聚合、注意力机制等）
1.3 研究内容与创新点：总结本文三大工作——多视角采集方案、注意力融合算法、基于大模型与RAG的智能检测系统

**强制约束**：
1. 必须且只能使用提供的引文文本进行引用
2. 引用格式为"姓名+年份"：中文文献用中文括弧如（作者 年份），英文文献用英文括弧如(Author Year)
3. 中文1名作者：（梅明华 1994）；2名作者：（梅明华和李泽炳 1995）；3+名作者：（梅明华等 1996）
4. 英文1名作者：(Smith 1990)；2名作者：(Smith and Jones 1992)；3+名作者：(Smith et al 1993)
5. 同一括弧多篇文献按年代排序，逗号分隔：(Smith 1990, Vaswani 2017)
6. 严禁编造不在可用引文列表中的引文
7. 使用学术写作风格，按小节组织内容
8. 字数不少于 3000 字
9. 用户提供的科研工作内容必须优先体现，特别是创新点部分

可用引文：{citation_texts}"""

CHAPTER1_HUMAN = """研究主题：{topic}

{research_context_section}

文献检索结果：
{literature_context}

可用引文：{citation_texts}

请撰写"1 绪论"章节完整内容（使用"姓名+年份"格式引用，中文文献如（梅明华 1994），英文文献如(Smith 1990)）："""


CHAPTER2_SYSTEM = """你是一个专业的中文学术论文写作助手。
根据提供的代码库检索结果和用户科研工作内容，撰写论文的"2 柑橘多视角图像采集与数据处理"章节。

**章节内容指引**：
2.1 多视角图像采集方案：
  - 基于旋转平台与双摄像头的采集装置设计
  - "4张水平环绕图 + 1张顶角图"的全覆盖拍摄流程
  - 采集参数设置（拍摄角度、光照条件等）
2.2 数据预处理与数据集构建：
  - 视频等间隔抽帧策略
  - 图像尺寸统一（224×224）处理流程
  - 数据增强方法（翻转、色彩抖动等）
  - 数据集划分（训练集/验证集/测试集比例与策略）

**重要约束**：
1. 只能基于提供的代码检索结果和用户科研内容进行描述，严禁编造代码中不存在的功能
2. 如果检索结果中没有相关信息，请明确说明
3. 使用清晰的技术术语和学术写作风格
4. 字数不少于 2500 字
5. 用户提供的科研工作内容必须优先体现"""

CHAPTER2_HUMAN = """研究主题：{topic}

{research_context_section}

代码检索结果：
{code_context}

请撰写"2 柑橘多视角图像采集与数据处理"章节完整内容："""


CHAPTER3_SYSTEM = """你是一个专业的中文学术论文写作助手。
根据提供的代码库检索结果和用户科研工作内容，撰写论文的"3 基于多视角注意力融合的检测模型构建"章节。

**章节内容指引**：
3.1 多视角注意力融合网络设计：
  - 以 ConvNeXt 为骨干网络的特征提取过程
  - 可学习位置编码的设计与实现
  - 多头自注意力机制（Multi-Head Attention）的特征融合过程
  - 分类头设计与输出
3.2 对比基线模型构建：
  - 单视角模型（Single-View）
  - 多视角简单拼接模型（Concat）
  - CNN-LSTM 序列模型
  - CNN-LSTM-Attention 模型
3.3 模型训练与优化策略：
  - 交叉熵损失函数
  - AdamW 优化器配置
  - 余弦退火学习率调度策略
  - 训练超参数设置（batch size、epoch、学习率等）

**重要约束**：
1. 只能基于提供的代码检索结果和用户科研内容进行描述，严禁编造代码中不存在的功能
2. 如果检索结果中没有相关信息，请明确说明
3. 使用清晰的技术术语和学术写作风格
4. 字数不少于 3500 字
5. 用户提供的模型架构、对比模型和训练策略必须优先体现"""

CHAPTER3_HUMAN = """研究主题：{topic}

{research_context_section}

代码检索结果：
{code_context}

请撰写"3 基于多视角注意力融合的检测模型构建"章节完整内容："""


CHAPTER4_SYSTEM = """你是一个专业的中文学术论文写作助手。
根据提供的代码库检索结果和用户科研工作内容，撰写论文的"4 实验结果与对比分析"章节。

**章节内容指引**：
4.1 实验环境与评估指标：
  - 软硬件环境（GPU型号、CUDA版本、深度学习框架等）
  - 评估指标定义（Accuracy、Precision、Recall、F1-Score）
4.2 多模型性能对比分析：
  - 5种模型在测试集上的性能对比表格
  - 重点分析注意力融合模型在保持高准确率的同时实现患虫样本100%召回率的优势
  - 各模型优劣势分析
4.3 特征可视化与机理分析：
  - Grad-CAM热力图分析，展示模型聚焦区域
  - 注意力权重分布可视化
  - 解释模型如何聚焦柑橘患虫关键区域

**重要约束**：
1. 只能基于提供的代码检索结果和用户科研内容进行描述，严禁编造代码中不存在的实验结果
2. 如果检索结果中没有相关信息，请明确说明
3. 使用清晰的技术术语和学术写作风格
4. 字数不少于 3000 字
5. 用户提供的实验指标和关键发现必须优先且准确体现，数值不可篡改"""

CHAPTER4_HUMAN = """研究主题：{topic}

{research_context_section}

代码检索结果：
{code_context}

请撰写"4 实验结果与对比分析"章节完整内容："""


CHAPTER5_SYSTEM = """你是一个专业的中文学术论文写作助手。
根据提供的代码库检索结果和用户科研工作内容，撰写论文的"5 柑橘实蝇智能检测与问答系统设计与实现"章节。

**章节内容指引**：
5.1 系统总体架构与交互设计：
  - 基于Flask的后端架构
  - 苹果毛玻璃风格（Glassmorphism）的响应式移动端/PC端UI设计
5.2 图像质量评估与智能检测模块：
  - 推理前的图像质量自动评估机制（清晰度、亮度、对比度等）
  - 调用ConvNeXt-Tiny模型进行离线推理的流程
5.3 基于大模型与RAG的智能问答模块：
  - 接入Qwen-plus大模型的实现
  - 本地RAG知识库（FAISS向量检索）构建与查询
  - 对检测结果的专业解读与病害防治问答功能
5.4 系统部署与公网访问：
  - 本地部署运行方案
  - 通过Ngrok/Cloudflare实现内网穿透与公网访问的工程实践

**重要约束**：
1. 只能基于提供的代码检索结果和用户科研内容进行描述，严禁编造代码中不存在的功能
2. 如果检索结果中没有相关信息，请明确说明
3. 使用清晰的技术术语和学术写作风格
4. 字数不少于 3000 字
5. 用户提供的系统架构和核心功能必须优先体现"""

CHAPTER5_HUMAN = """研究主题：{topic}

{research_context_section}

代码检索结果：
{code_context}

请撰写"5 柑橘实蝇智能检测与问答系统设计与实现"章节完整内容："""


CHAPTER6_SYSTEM = """你是一个专业的中文学术论文写作助手。
根据提供的研究主题、文献检索结果、代码检索结果和用户科研工作内容，撰写论文的"6 总结与展望"章节。

**章节内容指引**：
6.1 全文总结：
  - 回顾从算法设计、对比实验到系统全栈开发的完整研究闭环
  - 总结多视角采集方案、注意力融合算法、智能检测系统三大贡献
6.2 研究不足与未来展望：
  - 当前数据集规模的局限性
  - 单一品种柑橘的局限性
  - 未来在边缘计算设备部署方向的潜力
  - 多模态数据融合方向的展望

**重要约束**：
1. 综合使用文献和代码检索结果
2. 引用格式为"姓名+年份"：中文文献用中文括弧如（作者 年份），英文文献用英文括弧如(Author Year)
3. 中文1名作者：（梅明华 1994）；2名作者：（梅明华和李泽炳 1995）；3+名作者：（梅明华等 1996）
4. 英文1名作者：(Smith 1990)；2名作者：(Smith and Jones 1992)；3+名作者：(Smith et al 1993)
5. 同一括弧多篇文献按年代排序，逗号分隔：(Smith 1990, Vaswani 2017)
6. 严禁编造不在可用引文列表中的引文
7. 总结要全面，展望要有前瞻性
8. 使用学术写作风格
9. 字数不少于 1500 字
10. 用户提供的创新点、研究不足和未来展望必须优先体现

可用引文：{citation_texts}"""

CHAPTER6_HUMAN = """研究主题：{topic}

{research_context_section}

文献检索结果：
{literature_context}

代码检索结果：
{code_context}

可用引文：{citation_texts}

请撰写"6 总结与展望"章节完整内容（使用"姓名+年份"格式引用，中文文献如（梅明华 1994），英文文献如(Smith 1990)）："""


def _retrieve_literature(retriever, queries: List[str], top_k: int = 3) -> str:
    results = []
    if retriever:
        for query in queries:
            try:
                query_results = retriever.query(query, top_k=top_k)
                results.extend([r['text'] for r in query_results])
            except Exception as e:
                print(f"文献检索失败 '{query}': {e}")
    return "\n\n".join(results[:8]) if results else "未找到相关文献"


def _retrieve_code(retriever, queries: List[str], top_k: int = 3) -> str:
    results = []
    if retriever:
        for query in queries:
            try:
                query_results = retriever.query(query, top_k=top_k)
                results.extend([r['text'] for r in query_results])
            except Exception as e:
                print(f"代码检索失败 '{query}': {e}")
    return "\n\n".join(results[:8]) if results else "未找到相关代码信息"


def _call_llm(llm, prompt_value):
    if llm:
        response = llm.invoke(prompt_value)
        return response.content if hasattr(response, 'content') else str(response)
    return "（需要 LLM 生成具体内容）"


def _build_research_context_section(context: Dict[str, Any], chapter: str) -> str:
    hint = _format_research_context(context, chapter)
    if "未提供" in hint:
        return ""
    return RESEARCH_CONTEXT_INSTRUCTION.format(research_context_hint=hint)


def write_chapter1(state: Dict[str, Any]) -> Dict[str, Any]:
    topic = state.get("topic", "")
    llm = state.get("llm")
    literature_retriever = state.get("literature_retriever")
    citation_keys = state.get("citation_keys", [])
    citation_texts = state.get("citation_texts", {})
    research_context = state.get("research_context", {})

    if not citation_keys:
        state["errors"].append("错误：citation_keys 为空，无法进行引用")

    literature_context = _retrieve_literature(literature_retriever, [
        f"{topic} 柑橘实蝇危害与无损检测",
        f"{topic} 农产品无损检测技术综述",
        f"{topic} 深度学习病虫害检测",
        f"{topic} 多视角图像融合技术"
    ])

    citation_texts_str = "\n".join(citation_texts.values())
    research_context_section = _build_research_context_section(research_context, "1")

    prompt = ChatPromptTemplate.from_messages([
        ("system", CHAPTER1_SYSTEM),
        ("human", CHAPTER1_HUMAN)
    ]).format(
        topic=topic,
        literature_context=literature_context,
        citation_texts=citation_texts_str,
        research_context_section=research_context_section
    )

    content = _call_llm(llm, prompt)
    state["drafts"]["1 绪论"] = content
    state["current_section"] = "1 绪论"
    print("完成 1 绪论 章节撰写")
    return state


def write_chapter2(state: Dict[str, Any]) -> Dict[str, Any]:
    topic = state.get("topic", "")
    llm = state.get("llm")
    code_retriever = state.get("code_retriever")
    research_context = state.get("research_context", {})

    code_context = _retrieve_code(code_retriever, [
        f"{topic} 图像采集方案 旋转平台",
        f"{topic} 数据预处理 抽帧 尺寸统一",
        f"{topic} 数据增强 翻转 色彩抖动",
        f"{topic} 数据集划分 训练集 验证集 测试集"
    ])

    research_context_section = _build_research_context_section(research_context, "2")

    prompt = ChatPromptTemplate.from_messages([
        ("system", CHAPTER2_SYSTEM),
        ("human", CHAPTER2_HUMAN)
    ]).format(topic=topic, code_context=code_context, research_context_section=research_context_section)

    content = _call_llm(llm, prompt)
    state["drafts"]["2 柑橘多视角图像采集与数据处理"] = content
    state["current_section"] = "2 柑橘多视角图像采集与数据处理"
    print("完成 2 柑橘多视角图像采集与数据处理 章节撰写")
    return state


def write_chapter3(state: Dict[str, Any]) -> Dict[str, Any]:
    topic = state.get("topic", "")
    llm = state.get("llm")
    code_retriever = state.get("code_retriever")
    research_context = state.get("research_context", {})

    code_context = _retrieve_code(code_retriever, [
        f"{topic} ConvNeXt 骨干网络 特征提取",
        f"{topic} 多头自注意力机制 Multi-Head Attention 位置编码",
        f"{topic} 对比基线模型 CNN-LSTM 单视角 拼接",
        f"{topic} 训练策略 AdamW 余弦退火 交叉熵损失"
    ])

    research_context_section = _build_research_context_section(research_context, "3")

    prompt = ChatPromptTemplate.from_messages([
        ("system", CHAPTER3_SYSTEM),
        ("human", CHAPTER3_HUMAN)
    ]).format(topic=topic, code_context=code_context, research_context_section=research_context_section)

    content = _call_llm(llm, prompt)
    state["drafts"]["3 基于多视角注意力融合的检测模型构建"] = content
    state["current_section"] = "3 基于多视角注意力融合的检测模型构建"
    print("完成 3 基于多视角注意力融合的检测模型构建 章节撰写")
    return state


def write_chapter4(state: Dict[str, Any]) -> Dict[str, Any]:
    topic = state.get("topic", "")
    llm = state.get("llm")
    code_retriever = state.get("code_retriever")
    research_context = state.get("research_context", {})

    code_context = _retrieve_code(code_retriever, [
        f"{topic} 实验环境 GPU 评估指标 Accuracy Precision Recall F1",
        f"{topic} 模型性能对比 混淆矩阵 测试结果",
        f"{topic} Grad-CAM 热力图 可视化 注意力权重"
    ])

    research_context_section = _build_research_context_section(research_context, "4")

    prompt = ChatPromptTemplate.from_messages([
        ("system", CHAPTER4_SYSTEM),
        ("human", CHAPTER4_HUMAN)
    ]).format(topic=topic, code_context=code_context, research_context_section=research_context_section)

    content = _call_llm(llm, prompt)
    state["drafts"]["4 实验结果与对比分析"] = content
    state["current_section"] = "4 实验结果与对比分析"
    print("完成 4 实验结果与对比分析 章节撰写")
    return state


def write_chapter5(state: Dict[str, Any]) -> Dict[str, Any]:
    topic = state.get("topic", "")
    llm = state.get("llm")
    code_retriever = state.get("code_retriever")
    research_context = state.get("research_context", {})

    code_context = _retrieve_code(code_retriever, [
        f"{topic} Flask 后端架构 API 路由",
        f"{topic} 图像质量评估 清晰度 亮度 对比度",
        f"{topic} RAG 知识库 FAISS 向量检索 Qwen 大模型问答",
        f"{topic} 系统部署 Ngrok Cloudflare 内网穿透"
    ])

    research_context_section = _build_research_context_section(research_context, "5")

    prompt = ChatPromptTemplate.from_messages([
        ("system", CHAPTER5_SYSTEM),
        ("human", CHAPTER5_HUMAN)
    ]).format(topic=topic, code_context=code_context, research_context_section=research_context_section)

    content = _call_llm(llm, prompt)
    state["drafts"]["5 柑橘实蝇智能检测与问答系统设计与实现"] = content
    state["current_section"] = "5 柑橘实蝇智能检测与问答系统设计与实现"
    print("完成 5 柑橘实蝇智能检测与问答系统设计与实现 章节撰写")
    return state


def write_chapter6(state: Dict[str, Any]) -> Dict[str, Any]:
    topic = state.get("topic", "")
    llm = state.get("llm")
    literature_retriever = state.get("literature_retriever")
    code_retriever = state.get("code_retriever")
    citation_texts = state.get("citation_texts", {})
    research_context = state.get("research_context", {})

    literature_context = _retrieve_literature(literature_retriever, [
        f"{topic} 边缘计算 部署 深度学习",
        f"{topic} 多模态数据融合 农产品检测展望"
    ])

    code_context = _retrieve_code(code_retriever, [
        f"{topic} 系统总结 模型训练 检测流程",
        f"{topic} 未来改进 边缘部署 模型优化"
    ])

    citation_texts_str = "\n".join(citation_texts.values())
    research_context_section = _build_research_context_section(research_context, "6")

    prompt = ChatPromptTemplate.from_messages([
        ("system", CHAPTER6_SYSTEM),
        ("human", CHAPTER6_HUMAN)
    ]).format(
        topic=topic,
        literature_context=literature_context,
        code_context=code_context,
        citation_texts=citation_texts_str,
        research_context_section=research_context_section
    )

    content = _call_llm(llm, prompt)
    state["drafts"]["6 总结与展望"] = content
    state["current_section"] = "6 总结与展望"
    print("完成 6 总结与展望 章节撰写")
    return state

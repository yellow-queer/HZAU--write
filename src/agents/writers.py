"""
通用章节写作模块 - 支持动态章节写作

本模块提供通用化的章节写作功能，不包含任何特定课题的硬编码内容。
所有章节名称、提示词、检索查询都从配置动态获取。
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime


DEFAULT_CHAPTER_CONFIGS: Dict[str, Dict[str, Any]] = {
    "write_chapter1": {
        "name": "1 绪论",
        "system_prompt": """你是一位学术论文写作专家，负责撰写论文的绪论章节。
请遵循以下要求：
1. 清晰阐述研究背景与意义
2. 系统综述国内外研究现状
3. 明确指出研究内容与创新点
4. 使用学术性语言，逻辑严谨
5. 适当引用相关文献支持论述""",
        "human_prompt": """请撰写论文的绪论章节。

研究主题：{topic}

研究概述：
{research_summary}

章节写作指引：
{chapter_prompt}

请基于以上信息，撰写完整的绪论章节。""",
        "needs_retrieval": True,
        "retrieval_type": "literature",
        "word_limit": 3000
    },
    "write_chapter2": {
        "name": "2 研究方法与数据",
        "system_prompt": """你是一位学术论文写作专家，负责撰写论文的研究方法与数据章节。
请遵循以下要求：
1. 详细描述数据采集与实验设计
2. 说明数据处理与预处理方法
3. 介绍研究材料与技术平台
4. 确保方法描述的可重复性
5. 必要时结合代码实现说明""",
        "human_prompt": """请撰写论文的研究方法与数据章节。

研究主题：{topic}

研究概述：
{research_summary}

方法论描述：
{methodology}

章节写作指引：
{chapter_prompt}

请基于以上信息，撰写完整的研究方法与数据章节。""",
        "needs_retrieval": True,
        "retrieval_type": "code",
        "word_limit": 4000
    },
    "write_chapter3": {
        "name": "3 模型设计与实现",
        "system_prompt": """你是一位学术论文写作专家，负责撰写论文的模型设计与实现章节。
请遵循以下要求：
1. 清晰描述整体架构设计
2. 详细说明核心模块与技术
3. 阐述创新点与技术优势
4. 结合公式或伪代码说明关键算法
5. 保持技术描述的准确性""",
        "human_prompt": """请撰写论文的模型设计与实现章节。

研究主题：{topic}

研究概述：
{research_summary}

方法论描述：
{methodology}

章节写作指引：
{chapter_prompt}

请基于以上信息，撰写完整的模型设计与实现章节。""",
        "needs_retrieval": True,
        "retrieval_type": "code",
        "word_limit": 5000
    },
    "write_chapter4": {
        "name": "4 实验结果与分析",
        "system_prompt": """你是一位学术论文写作专家，负责撰写论文的实验结果与分析章节。
请遵循以下要求：
1. 清晰呈现实验设置与环境
2. 系统展示对比实验结果
3. 深入分析实验数据与发现
4. 使用表格或图表辅助说明
5. 客观评价方法的优势与局限""",
        "human_prompt": """请撰写论文的实验结果与分析章节。

研究主题：{topic}

研究概述：
{research_summary}

实验结果：
{experiment_results}

章节写作指引：
{chapter_prompt}

请基于以上信息，撰写完整的实验结果与分析章节。""",
        "needs_retrieval": True,
        "retrieval_type": "code",
        "word_limit": 5000
    },
    "write_chapter5": {
        "name": "5 系统开发与应用",
        "system_prompt": """你是一位学术论文写作专家，负责撰写论文的系统开发与应用章节。
请遵循以下要求：
1. 描述系统需求与设计目标
2. 说明系统架构与技术选型
3. 介绍核心功能实现
4. 展示系统界面与应用效果
5. 讨论部署方案与实际应用""",
        "human_prompt": """请撰写论文的系统开发与应用章节。

研究主题：{topic}

研究概述：
{research_summary}

系统实现描述：
{system_implementation}

章节写作指引：
{chapter_prompt}

请基于以上信息，撰写完整的系统开发与应用章节。""",
        "needs_retrieval": True,
        "retrieval_type": "code",
        "word_limit": 4000
    },
    "write_chapter6": {
        "name": "6 总结与展望",
        "system_prompt": """你是一位学术论文写作专家，负责撰写论文的总结与展望章节。
请遵循以下要求：
1. 凝练总结主要研究工作与贡献
2. 客观指出研究的不足之处
3. 清晰展望未来的研究方向
4. 保持语言简洁、层次分明
5. 避免引入新的技术细节""",
        "human_prompt": """请撰写论文的总结与展望章节。

研究主题：{topic}

研究概述：
{research_summary}

研究不足与展望：
{limitations_and_future}

章节写作指引：
{chapter_prompt}

请基于以上信息，撰写完整的总结与展望章节。""",
        "needs_retrieval": False,
        "retrieval_type": None,
        "word_limit": 2000
    }
}


def get_chapter_name(chapter_num: str, research_context: Dict[str, Any]) -> str:
    """
    获取章节名称
    
    Args:
        chapter_num: 章节编号，如 "write_chapter1"
        research_context: 研究上下文配置
        
    Returns:
        章节名称字符串
    """
    chapters = research_context.get("chapters", {})
    return chapters.get(chapter_num, DEFAULT_CHAPTER_CONFIGS[chapter_num]["name"])


def get_chapter_system_prompt(
    chapter_num: str,
    chapter_name: str,
    research_context: Dict[str, Any]
) -> str:
    """
    生成系统提示词
    
    Args:
        chapter_num: 章节编号
        chapter_name: 章节名称
        research_context: 研究上下文配置
        
    Returns:
        系统提示词字符串
    """
    chapter_config = DEFAULT_CHAPTER_CONFIGS.get(chapter_num, {})
    base_prompt = chapter_config.get("system_prompt", "")
    
    return f"""{base_prompt}

当前章节：{chapter_name}
研究主题：{research_context.get('title', '未命名研究')}"""


def get_chapter_human_prompt(
    chapter_num: str,
    chapter_name: str,
    research_context: Dict[str, Any],
    chapter_prompts: Optional[Dict[str, str]] = None
) -> str:
    """
    生成用户提示词
    
    Args:
        chapter_num: 章节编号
        chapter_name: 章节名称
        research_context: 研究上下文配置
        chapter_prompts: 可选的自定义章节提示词覆盖
        
    Returns:
        用户提示词字符串
    """
    chapter_config = DEFAULT_CHAPTER_CONFIGS.get(chapter_num, {})
    base_prompt = chapter_config.get("human_prompt", "")
    
    topic = research_context.get("title", "未命名研究")
    research_summary = research_context.get("research_summary", "")
    
    chapter_prompt = ""
    if chapter_prompts and chapter_num in chapter_prompts:
        chapter_prompt = chapter_prompts[chapter_num]
    else:
        chapter_prompt = f"请按照学术论文规范撰写{chapter_name}章节"
    
    methodology = research_context.get("methodology", {})
    if isinstance(methodology, dict):
        methodology_str = ""
        for key, value in methodology.items():
            if isinstance(value, str):
                methodology_str += f"{key}: {value}\n"
        methodology = methodology_str
    elif isinstance(methodology, str):
        methodology = methodology
    else:
        methodology = ""
    
    experiment_results = research_context.get("experiment_results", {})
    if isinstance(experiment_results, dict):
        results_str = ""
        for key, value in experiment_results.items():
            if isinstance(value, str):
                results_str += f"{key}: {value}\n"
            elif isinstance(value, dict):
                results_str += f"{key}:\n"
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, str):
                        results_str += f"  {sub_key}: {sub_value}\n"
        experiment_results = results_str
    elif isinstance(experiment_results, str):
        experiment_results = experiment_results
    else:
        experiment_results = ""
    
    system_implementation = research_context.get("system_implementation", {})
    if isinstance(system_implementation, dict):
        impl_str = ""
        for key, value in system_implementation.items():
            if isinstance(value, str):
                impl_str += f"{key}: {value}\n"
            elif isinstance(value, list):
                impl_str += f"{key}:\n"
                for item in value:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            impl_str += f"  - {k}: {v}\n"
                    elif isinstance(item, str):
                        impl_str += f"  - {item}\n"
        system_implementation = impl_str
    elif isinstance(system_implementation, str):
        system_implementation = system_implementation
    else:
        system_implementation = ""
    
    limitations_and_future = research_context.get("limitations_and_future", {})
    if isinstance(limitations_and_future, dict):
        lim_str = ""
        if "limitations" in limitations_and_future:
            lim_str += "研究不足:\n"
            for item in limitations_and_future["limitations"]:
                if isinstance(item, str):
                    lim_str += f"  - {item}\n"
        if "future_work" in limitations_and_future:
            lim_str += "未来工作方向:\n"
            for item in limitations_and_future["future_work"]:
                if isinstance(item, str):
                    lim_str += f"  - {item}\n"
        limitations_and_future = lim_str
    elif isinstance(limitations_and_future, str):
        limitations_and_future = limitations_and_future
    else:
        limitations_and_future = ""
    
    prompt = base_prompt.format(
        topic=topic,
        research_summary=research_summary,
        chapter_prompt=chapter_prompt,
        methodology=methodology,
        experiment_results=experiment_results,
        system_implementation=system_implementation,
        limitations_and_future=limitations_and_future
    )
    
    return prompt


def get_retrieval_queries(
    chapter_num: str,
    topic: str,
    research_context: Dict[str, Any],
    retrieval_queries: Optional[Dict[str, Dict[str, List[str]]]] = None
) -> Dict[str, List[str]]:
    """
    获取检索查询
    
    Args:
        chapter_num: 章节编号
        topic: 研究主题
        research_context: 研究上下文配置
        retrieval_queries: 可选的自定义检索查询配置
        
    Returns:
        检索查询字典，包含 "literature"、"code" 和 "content" 三个键
    """
    result = {"literature": [], "code": [], "content": []}
    
    if retrieval_queries and chapter_num in retrieval_queries:
        chapter_queries = retrieval_queries[chapter_num]
        if "literature" in chapter_queries:
            result["literature"] = chapter_queries["literature"]
        if "code" in chapter_queries:
            result["code"] = chapter_queries["code"]
        if "content" in chapter_queries:
            result["content"] = chapter_queries["content"]
        return result
    
    chapter_config = DEFAULT_CHAPTER_CONFIGS.get(chapter_num, {})
    retrieval_type = chapter_config.get("retrieval_type", "literature")
    
    if retrieval_type == "literature":
        result["literature"] = [
            f"{topic} 研究背景",
            f"{topic} 相关研究",
            f"{topic} 技术方法"
        ]
    elif retrieval_type == "code":
        result["code"] = [
            f"{topic} 核心实现",
            f"{topic} 数据处理",
            f"{topic} 模型代码"
        ]
    
    result["content"] = [
        f"{topic} 实验结果",
        f"{topic} 数据分析",
        f"{topic} 项目介绍"
    ]
    
    return result


def _perform_retrieval(
    state: Dict[str, Any],
    queries: Dict[str, List[str]],
    chapter_name: str
) -> str:
    """
    执行检索并格式化结果
    
    Args:
        state: 当前状态
        queries: 检索查询
        chapter_name: 章节名称
        
    Returns:
        格式化的检索结果字符串
    """
    retrieval_results = []
    
    literature_retriever = state.get("literature_retriever")
    code_retriever = state.get("code_retriever")
    content_retriever = state.get("content_retriever")
    
    research_context = state.get("research_context", {})
    content_chapter_keys = research_context.get("content_chapter_keys", [
        "write_chapter2", "write_chapter3", "write_chapter4", "write_chapter5"
    ])
    chapters = research_context.get("chapters", {})
    content_chapter_names = [chapters.get(key, key) for key in content_chapter_keys]
    should_retrieve_content = chapter_name in content_chapter_names
    
    if queries.get("literature") and literature_retriever:
        for query in queries["literature"]:
            try:
                results = literature_retriever.query(query, top_k=3)
                if results:
                    retrieval_results.append(results)
            except Exception as e:
                print(f"⚠ 文献检索失败 '{query}': {e}")
    
    if queries.get("code") and code_retriever:
        for query in queries["code"]:
            try:
                results = code_retriever.query(query, top_k=3)
                if results:
                    retrieval_results.append(results)
            except Exception as e:
                print(f"⚠ 代码检索失败 '{query}': {e}")
    
    if should_retrieve_content and queries.get("content") and content_retriever:
        for query in queries["content"]:
            try:
                results = content_retriever.query(query, top_k=3)
                if results:
                    retrieval_results.append(results)
            except Exception as e:
                print(f"⚠ 内容检索失败 '{query}': {e}")
    
    if retrieval_results:
        return "\n\n".join(retrieval_results)
    return ""


def _write_chapter(
    state: Dict[str, Any],
    chapter_num: str,
    chapter_prompts: Optional[Dict[str, str]] = None,
    retrieval_queries: Optional[Dict[str, Dict[str, List[str]]]] = None
) -> Dict[str, Any]:
    """
    通用章节写作函数
    
    Args:
        state: 当前状态
        chapter_num: 章节编号
        chapter_prompts: 可选的自定义章节提示词覆盖
        retrieval_queries: 可选的自定义检索查询覆盖
        
    Returns:
        更新后的状态
    """
    research_context = state.get("research_context", {})
    topic = research_context.get("title", "未命名研究")
    
    chapter_name = get_chapter_name(chapter_num, research_context)
    
    print(f"\n正在撰写：{chapter_name}")
    
    chapter_config = DEFAULT_CHAPTER_CONFIGS.get(chapter_num, {})
    needs_retrieval = chapter_config.get("needs_retrieval", False)
    
    retrieval_context = ""
    if needs_retrieval:
        queries = get_retrieval_queries(
            chapter_num,
            topic,
            research_context,
            retrieval_queries
        )
        retrieval_context = _perform_retrieval(state, queries, chapter_name)
        if retrieval_context:
            print(f"✓ 检索到相关文献和代码信息")
    
    system_prompt = get_chapter_system_prompt(chapter_num, chapter_name, research_context)
    human_prompt = get_chapter_human_prompt(
        chapter_num,
        chapter_name,
        research_context,
        chapter_prompts
    )
    
    if retrieval_context:
        human_prompt += f"\n\n参考资料:\n{retrieval_context}"
    
    llm = state.get("llm")
    if llm is None:
        raise ValueError("LLM 未初始化，请检查 qwen_config.py 配置")
    
    word_limit = chapter_config.get("word_limit", 3000)
    additional_notes = research_context.get("additional_notes", "")
    
    full_prompt = f"""{human_prompt}

写作要求:
- 字数要求：约{word_limit}字
- 使用规范的学术语言
- 逻辑清晰，层次分明
- 图表、公式使用 LaTeX 格式
- 将参考资料自然融入正文，不要出现"根据某文件"、"某文档中提到"等引用标识
- 避免在正文中标注文件来源或路径

{additional_notes if additional_notes else ""}"""
    
    try:
        response = llm.invoke(f"{system_prompt}\n\n{full_prompt}")
        content = response.content if hasattr(response, "content") else str(response)
        
        drafts = state.get("drafts", {})
        drafts[chapter_name] = content
        state["drafts"] = drafts
        
        print(f"✓ {chapter_name} 撰写完成")
        
        return state
        
    except Exception as e:
        print(f"❌ 章节撰写失败：{chapter_name}")
        print(f"错误：{e}")
        raise


def write_chapter1(
    state: Dict[str, Any],
    chapter_prompts: Optional[Dict[str, str]] = None,
    retrieval_queries: Optional[Dict[str, Dict[str, List[str]]]] = None
) -> Dict[str, Any]:
    """
    撰写第 1 章：绪论
    
    Args:
        state: 当前状态
        chapter_prompts: 可选的自定义章节提示词覆盖
        retrieval_queries: 可选的自定义检索查询覆盖
        
    Returns:
        更新后的状态
    """
    return _write_chapter(state, "write_chapter1", chapter_prompts, retrieval_queries)


def write_chapter2(
    state: Dict[str, Any],
    chapter_prompts: Optional[Dict[str, str]] = None,
    retrieval_queries: Optional[Dict[str, Dict[str, List[str]]]] = None
) -> Dict[str, Any]:
    """
    撰写第 2 章：研究方法与数据
    
    Args:
        state: 当前状态
        chapter_prompts: 可选的自定义章节提示词覆盖
        retrieval_queries: 可选的自定义检索查询覆盖
        
    Returns:
        更新后的状态
    """
    return _write_chapter(state, "write_chapter2", chapter_prompts, retrieval_queries)


def write_chapter3(
    state: Dict[str, Any],
    chapter_prompts: Optional[Dict[str, str]] = None,
    retrieval_queries: Optional[Dict[str, Dict[str, List[str]]]] = None
) -> Dict[str, Any]:
    """
    撰写第 3 章：模型设计与实现
    
    Args:
        state: 当前状态
        chapter_prompts: 可选的自定义章节提示词覆盖
        retrieval_queries: 可选的自定义检索查询覆盖
        
    Returns:
        更新后的状态
    """
    return _write_chapter(state, "write_chapter3", chapter_prompts, retrieval_queries)


def write_chapter4(
    state: Dict[str, Any],
    chapter_prompts: Optional[Dict[str, str]] = None,
    retrieval_queries: Optional[Dict[str, Dict[str, List[str]]]] = None
) -> Dict[str, Any]:
    """
    撰写第 4 章：实验结果与分析
    
    Args:
        state: 当前状态
        chapter_prompts: 可选的自定义章节提示词覆盖
        retrieval_queries: 可选的自定义检索查询覆盖
        
    Returns:
        更新后的状态
    """
    return _write_chapter(state, "write_chapter4", chapter_prompts, retrieval_queries)


def write_chapter5(
    state: Dict[str, Any],
    chapter_prompts: Optional[Dict[str, str]] = None,
    retrieval_queries: Optional[Dict[str, Dict[str, List[str]]]] = None
) -> Dict[str, Any]:
    """
    撰写第 5 章：系统开发与应用
    
    Args:
        state: 当前状态
        chapter_prompts: 可选的自定义章节提示词覆盖
        retrieval_queries: 可选的自定义检索查询覆盖
        
    Returns:
        更新后的状态
    """
    return _write_chapter(state, "write_chapter5", chapter_prompts, retrieval_queries)


def write_chapter6(
    state: Dict[str, Any],
    chapter_prompts: Optional[Dict[str, str]] = None,
    retrieval_queries: Optional[Dict[str, Dict[str, List[str]]]] = None
) -> Dict[str, Any]:
    """
    撰写第 6 章：总结与展望
    
    Args:
        state: 当前状态
        chapter_prompts: 可选的自定义章节提示词覆盖
        retrieval_queries: 可选的自定义检索查询覆盖
        
    Returns:
        更新后的状态
    """
    return _write_chapter(state, "write_chapter6", chapter_prompts, retrieval_queries)

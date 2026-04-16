"""
AutoPaperGen - 学术论文初稿自动生成系统

基于给定的研究主题、用户科研工作内容、项目代码库、参考文献库，
自动生成符合指定模板格式的论文初稿。

用法:
    python main.py <研究主题> [模板路径] [--context 科研内容文件]

示例:
    python main.py "基于深度学习的图像分类" data/templates/hzau_thesis.md --context data/research_context.yaml
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from src.workflow_hzau import create_workflow
from src.render import render_final_paper, create_default_template
from src.rag.lit_index import LiteratureIndex
from src.rag.code_index import CodebaseIndex
from src.utils.qwen_config import create_qwen_llm, get_qwen_embedding_model, load_qwen_config


def load_research_context(context_path: str) -> Dict[str, Any]:
    """
    加载用户科研工作内容
    
    Args:
        context_path: YAML 文件路径
    
    Returns:
        科研内容字典
    """
    path = Path(context_path)
    if not path.exists():
        print(f"警告：科研内容文件不存在：{context_path}")
        return {}
    
    with open(path, 'r', encoding='utf-8') as f:
        context = yaml.safe_load(f)
    
    print(f"已加载科研工作内容：{path.name}")
    
    if context:
        summary = context.get('research_summary', '')
        innovations = context.get('innovations', [])
        print(f"  研究概述：{summary[:80]}..." if len(summary) > 80 else f"  研究概述：{summary}")
        print(f"  创新点数量：{len(innovations)}")
    
    return context if context else {}


def run(
    topic: str,
    template_path: Optional[str] = None,
    context_path: Optional[str] = None,
    llm=None,
    embed_model=None,
    use_qwen: bool = True
) -> str:
    """
    运行 AutoPaperGen 系统
    
    Args:
        topic: 研究主题
        template_path: 论文模板文件路径（可选）
        context_path: 用户科研工作内容文件路径（可选，YAML 格式）
        llm: LLM 模型（可选）
        embed_model: 嵌入模型（可选）
        use_qwen: 是否使用 Qwen API（默认 True）
    
    Returns:
        生成的论文文件路径
    """
    print(f"开始生成论文：{topic}")
    print("=" * 50)
    
    # 加载用户科研工作内容
    research_context = {}
    if context_path:
        research_context = load_research_context(context_path)
    else:
        default_context = Path("data/research_context.yaml")
        if default_context.exists():
            print(f"发现默认科研内容文件：{default_context}")
            research_context = load_research_context(str(default_context))
    
    # 如果科研内容中有标题，覆盖 topic
    if research_context.get('title'):
        topic = research_context['title']
        print(f"使用科研内容中的标题：{topic}")
    
    # 初始化 LLM 和嵌入模型
    if use_qwen and llm is None:
        print("正在初始化 Qwen API...")
        try:
            config = load_qwen_config()
            print(f"使用模型：{config['model']}")
            llm = create_qwen_llm(model=config["model"])
            embed_model = get_qwen_embedding_model()
        except Exception as e:
            print(f"警告：Qwen API 初始化失败：{e}")
            print("将使用默认配置（需要本地安装相关依赖）")
    
    # 如果没有提供模板路径，创建默认模板
    if template_path is None:
        print("未提供模板路径，创建默认 Markdown 模板...")
        template_path = create_default_template(template_type="markdown")
    
    # 初始化 RAG 索引
    print("初始化 RAG 检索器...")
    lit_index = LiteratureIndex(
        literature_dir="data/literature",
        persist_dir=".chroma_literature"
    )
    lit_index.parse_literature_files()
    lit_index.build_index(llm=llm, embed_model=embed_model)
    
    code_index = CodebaseIndex(
        codebase_dir="data/codebase",
        persist_dir=".chroma_codebase"
    )
    code_index.build_index(llm=llm, embed_model=embed_model)
    
    # 创建工作流
    workflow = create_workflow()
    
    # 初始化状态并运行工作流
    citation_texts = lit_index.generate_citation_texts()

    initial_state = {
        "topic": topic,
        "citation_keys": lit_index.get_valid_citation_keys(),
        "citation_texts": citation_texts,
        "outline": {},
        "drafts": {},
        "errors": [],
        "current_section": "",
        "max_retries": 3,
        "retries": 0,
        "sections_to_rewrite": [],
        "llm": llm,
        "literature_retriever": lit_index,
        "code_retriever": code_index,
        "style_retriever": None,
        "research_context": research_context
    }
    
    print("执行工作流...")
    print(f"合法的 Citation Keys: {initial_state['citation_keys']}")
    if citation_texts:
        print(f"可用引文文本：{', '.join(citation_texts.values())}")
    if research_context:
        print(f"用户科研内容已加载，包含 {len(research_context)} 个字段")
    print("=" * 50)
    
    final_state = workflow.invoke(initial_state)
    
    # 检查是否有错误
    if final_state.get("errors"):
        print("\n警告：生成过程中出现以下错误:")
        for error in final_state["errors"]:
            print(f"  - {error}")
    
    # 渲染最终论文
    print("\n渲染最终论文...")
    output_path = render_final_paper(
        template_path=template_path,
        drafts=final_state["drafts"]
    )
    
    print(f"论文已生成：{output_path}")
    return output_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AutoPaperGen - 学术论文初稿自动生成系统")
    parser.add_argument("topic", help="研究主题")
    parser.add_argument("template_path", nargs="?", default=None, help="论文模板路径（可选）")
    parser.add_argument("--context", "-c", default=None, help="用户科研工作内容文件路径（YAML 格式）")
    
    args = parser.parse_args()
    
    output_file = run(
        topic=args.topic,
        template_path=args.template_path,
        context_path=args.context
    )
    print(f"\n完成！论文已保存到：{output_file}")

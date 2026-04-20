"""
模板渲染模块

使用 Jinja2 将生成的章节草稿注入到用户指定的模板中
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Template, FileSystemLoader, Environment

from src.agents.planner import DEFAULT_CHAPTER_NAMES


def get_chapter_variable_name(chapter_name: str) -> str:
    """
    将章节名称转换为模板变量名
    
    Args:
        chapter_name: 章节名称（如 "1 绪论", "2 柑橘多视角图像采集与数据处理"）
    
    Returns:
        变量名（如 "chapter_1", "chapter_2"）
    
    Examples:
        >>> get_chapter_variable_name("1 绪论")
        'chapter_1'
        >>> get_chapter_variable_name("2 柑橘多视角图像采集与数据处理")
        'chapter_2'
    """
    match = re.match(r'^(\d+)', chapter_name.strip())
    if match:
        chapter_num = match.group(1)
        return f"chapter_{chapter_num}"
    else:
        chapter_num = re.sub(r'[^\w]', '_', chapter_name)
        return f"chapter_{chapter_num}"


def _generate_references_list(drafts: Dict[str, str]) -> str:
    import re
    all_citations = []
    seen = set()
    for content in drafts.values():
        cn_citations = re.findall(r'（[^）]+\d{4}）', content)
        en_citations = re.findall(r'\([^)]*?\d{4}\)', content)
        for c in cn_citations + en_citations:
            if c not in seen:
                seen.add(c)
                all_citations.append(c)
    all_citations.sort(key=lambda x: re.search(r'\d{4}', x).group() if re.search(r'\d{4}', x) else '0')
    return '\n'.join(all_citations)


def render_final_paper(
    template_path: str, 
    drafts: Dict[str, str], 
    output_dir: str = "output",
    chapters: Optional[Dict[str, str]] = None
) -> str:
    """
    渲染最终论文
    
    Args:
        template_path: 模板文件路径
        drafts: 各章节草稿（章节名 -> 内容）
        output_dir: 输出目录
        chapters: 章节名称映射字典（draft_key -> chapter_name）
                 如 {"write_chapter1": "1 绪论", "write_chapter2": "2 研究方法与数据"}
    
    Returns:
        输出文件路径
    """
    if chapters is None:
        chapters = DEFAULT_CHAPTER_NAMES
    
    # 确保输出目录存在
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 读取模板文件
    template_file = Path(template_path)
    if not template_file.exists():
        raise FileNotFoundError(f"模板文件不存在：{template_path}")
    
    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # 创建 Jinja2 模板
    template = Template(template_content)
    
    # 准备渲染上下文 - 动态构建章节映射
    context = {'drafts': drafts}
    
    # 动态添加章节内容到上下文
    for draft_key, chapter_name in chapters.items():
        var_name = get_chapter_variable_name(chapter_name)
        context[var_name] = drafts.get(chapter_name, '')
    
    # 添加其他固定字段
    context.update({
        'keywords': drafts.get('关键词', ''),
        'english_abstract': drafts.get('英文摘要', ''),
        'english_keywords': drafts.get('英文关键词', ''),
        'references': drafts.get('参考文献', ''),
        'acknowledgements': drafts.get('致谢', ''),
        'references_list': _generate_references_list(drafts)
    })
    
    # 渲染模板
    rendered_content = template.render(**context)
    
    # 确定输出文件名
    output_filename = f"paper{template_file.suffix}"
    output_file = output_path / output_filename
    
    # 保存渲染后的内容
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(rendered_content)
    
    print(f"论文已渲染并保存到：{output_file}")
    return str(output_file)


def create_default_template(
    template_type: str = "markdown", 
    output_path: str = "data/templates",
    chapters: Optional[Dict[str, str]] = None
) -> str:
    """
    创建默认模板
    
    Args:
        template_type: 模板类型（"markdown" 或 "latex"）
        output_path: 输出路径
        chapters: 章节名称映射字典（draft_key -> chapter_name）
                 如 {"write_chapter1": "1 绪论", "write_chapter2": "2 研究方法与数据"}
    
    Returns:
        创建的模板文件路径
    """
    if chapters is None:
        chapters = {
            "write_chapter1": "1 绪论",
            "write_chapter2": "2 柑橘多视角图像采集与数据处理",
            "write_chapter3": "3 基于多视角注意力融合的检测模型构建",
            "write_chapter4": "4 实验结果与对比分析",
            "write_chapter5": "5 柑橘实蝇智能检测与问答系统设计与实现",
            "write_chapter6": "6 总结与展望",
        }
    
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 动态生成章节模板内容
    chapter_sections = []
    for draft_key, chapter_name in chapters.items():
        var_name = get_chapter_variable_name(chapter_name)
        chapter_sections.append((chapter_name, var_name))
    
    if template_type == "latex":
        # 动态生成 LaTeX 章节
        chapter_blocks = []
        for chapter_name, var_name in chapter_sections:
            chapter_title = chapter_name.split(' ', 1)[1] if ' ' in chapter_name else chapter_name
            chapter_blocks.append(f"\\section{{{chapter_title}}}\n{{{{ {var_name} }}}}")
        
        template_content = r"""\documentclass[12pt]{article}
\usepackage{amsmath}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{ctex}

\title{AutoPaperGen 生成的论文}
\author{AutoPaperGen 系统}
\date{\today}

\begin{document}

\maketitle

\begin{abstract}
{{ english_abstract }}
\end{abstract}

""" + "\n\n".join(chapter_blocks) + r"""

\end{document}
"""
        template_file = output_dir / "template.tex"
    else:  # markdown
        # 动态生成 Markdown 章节
        chapter_blocks = []
        for chapter_name, var_name in chapter_sections:
            chapter_blocks.append(f"## {chapter_name}\n\n{{{{ {var_name} }}}}")
        
        template_content = f"""# {{{{ title | default('AutoPaperGen 生成的论文') }}}}

## 关键词

{{{{ keywords }}}}

## 英文摘要

{{{{ english_abstract }}}}

## 英文关键词

{{{{ english_keywords }}}}

""" + "\n\n".join(chapter_blocks) + f"""

## 参考文献

{{{{ references }}}}

## 致谢

{{{{ acknowledgements }}}}

---
*Generated by AutoPaperGen*
"""
        template_file = output_dir / "template.md"
    
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"已创建默认模板：{template_file}")
    return str(template_file)

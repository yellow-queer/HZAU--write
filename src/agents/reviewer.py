import re
from typing import Dict, Any, List, Set, Optional, TypedDict


class CitationWarning(TypedDict):
    chapter: str
    citation: str
    context: str
    reason: str
    position: str


def get_citation_context(text: str, citation: str, context_length: int = 50) -> str:
    pos = text.find(citation)
    if pos == -1:
        return "未找到上下文"
    
    start = max(0, pos - context_length)
    end = min(len(text), pos + len(citation) + context_length)
    
    context = text[start:end]
    
    if start > 0:
        context = "..." + context
    if end < len(text):
        context = context + "..."
    
    return context


def get_citation_position(text: str, citation: str) -> str:
    pos = text.find(citation)
    if pos == -1:
        return "位置未知"
    
    text_before = text[:pos]
    paragraphs = text_before.split('\n\n')
    paragraph_num = len(paragraphs)
    
    lines_before = text_before.split('\n')
    line_num = len(lines_before) + 1
    
    char_in_paragraph = pos - text_before.rfind('\n\n') - 2 if '\n\n' in text_before else pos
    
    return f"第 {paragraph_num} 段，约第 {char_in_paragraph + 1} 字符"


def format_citation_warning(warning: CitationWarning, index: int) -> str:
    return (
        f"⚠️ 引文警告 #{index}：\n"
        f"  章节：{warning['chapter']}\n"
        f"  引文：{warning['citation']}\n"
        f"  位置：{warning['position']}\n"
        f"  原因：{warning['reason']}\n"
        f"  上下文：{warning['context']}"
    )


def normalize_citation(citation_text: str) -> str:
    normalized = citation_text
    normalized = normalized.replace('（', '(').replace('）', ')')
    normalized = re.sub(r'\s+', ' ', normalized)
    normalized = re.sub(r'\(\s+', '(', normalized)
    normalized = re.sub(r'\s+\)', ')', normalized)
    normalized = re.sub(r'\bet al\.,?', 'et al', normalized)
    normalized = normalized.strip()
    return normalized


def split_combined_citations(citation_text: str) -> List[str]:
    inner_match = re.match(r'^([（(])(.+)([）)])$', citation_text.strip())
    if not inner_match:
        return [citation_text]
    
    open_bracket = inner_match.group(1)
    inner_content = inner_match.group(2)
    close_bracket = inner_match.group(3)
    
    parts = re.split(r'[;；]', inner_content)
    
    if len(parts) <= 1:
        return [citation_text]
    
    individual_citations = []
    for part in parts:
        part = part.strip()
        if part:
            individual_citations.append(f"{open_bracket}{part}{close_bracket}")
    
    return individual_citations if individual_citations else [citation_text]


def validate_single_citation(citation_text: str, valid_texts: Set[str]) -> Dict[str, Any]:
    normalized = normalize_citation(citation_text)
    
    normalized_valid_texts = {normalize_citation(v): v for v in valid_texts}
    
    if normalized in normalized_valid_texts:
        return {
            "is_valid": True,
            "normalized": normalized,
            "matched": normalized_valid_texts[normalized]
        }
    
    for norm_key, original in normalized_valid_texts.items():
        if normalized == norm_key:
            return {
                "is_valid": True,
                "normalized": normalized,
                "matched": original
            }
    
    return {
        "is_valid": False,
        "normalized": normalized,
        "matched": None
    }


def extract_all_citations(text: str) -> List[str]:
    cn_pattern = r'（[^）]+\d{4}[^）]*）'
    en_pattern = r'\([^)]*?\d{4}[^)]*\)'
    cn_matches = re.findall(cn_pattern, text)
    en_matches = re.findall(en_pattern, text)
    return cn_matches + en_matches


def check_citations(state: Dict[str, Any]) -> Dict[str, Any]:
    print("\n" + "=" * 60)
    print("开始引文检查...")
    print("=" * 60)

    citation_texts = state.get("citation_texts", {})
    drafts = state.get("drafts", {})
    errors = state.get("errors", [])

    errors = []
    warnings: List[CitationWarning] = []

    valid_citation_texts = set(citation_texts.values())
    print(f"\n[引文库信息]")
    print(f"  已加载合法引文数量: {len(valid_citation_texts)}")

    hallucinated_citations: Dict[str, List[str]] = {}

    total_citations_extracted = 0
    total_valid = 0
    total_invalid = 0

    for section_name, content in drafts.items():
        if not content:
            print(f"\n[章节 '{section_name}'] 内容为空，跳过检查")
            continue

        print(f"\n[章节 '{section_name}'] 开始检查...")
        citations = extract_all_citations(content)
        total_citations_extracted += len(citations)
        print(f"  提取到引文数量: {len(citations)}")

        if citations:
            sample_citations = citations[:5]
            print(f"  引文示例 (前{len(sample_citations)}个):")
            for i, c in enumerate(sample_citations, 1):
                normalized = normalize_citation(c)
                print(f"    {i}. 原始: '{c}' -> 标准化: '{normalized}'")

        invalid_citations = []
        for c in citations:
            split_citations = split_combined_citations(c)

            for single_c in split_citations:
                result = validate_single_citation(single_c, valid_citation_texts)

                if not result["is_valid"]:
                    invalid_citations.append(single_c)
                    total_invalid += 1
                    
                    context = get_citation_context(content, single_c)
                    position = get_citation_position(content, single_c)
                    reason = f"引文不在文献库中（标准化后: '{result['normalized']}'，在 {len(valid_citation_texts)} 个合法引文中未找到匹配）"
                    
                    warning: CitationWarning = {
                        "chapter": section_name,
                        "citation": single_c,
                        "context": context,
                        "reason": reason,
                        "position": position
                    }
                    warnings.append(warning)
                else:
                    total_valid += 1

        if invalid_citations:
            hallucinated_citations[section_name] = invalid_citations
            print(f"\n  章节 '{section_name}' 发现 {len(invalid_citations)} 个可疑引文")
        else:
            print(f"\n  ✓ 章节 '{section_name}' 引文检查通过")

    print("\n" + "=" * 60)
    print("[引文检查统计]")
    print(f"  总提取引文数: {total_citations_extracted}")
    print(f"  合法引文数: {total_valid}")
    print(f"  可疑引文数: {total_invalid}")
    print("=" * 60)

    if warnings:
        print(f"\n⚠️ 共发现 {len(warnings)} 个引文警告，详情如下：")
        print("-" * 60)
        for i, warning in enumerate(warnings, 1):
            print(format_citation_warning(warning, i))
            print("-" * 60)

    state["errors"] = errors
    state["citation_warnings"] = warnings

    if hallucinated_citations:
        print(f"\n发现可疑引文章节: {list(hallucinated_citations.keys())}")
        state["sections_to_rewrite"] = list(hallucinated_citations.keys())
    else:
        print("\n✓ 所有章节引文检查通过")
        state["sections_to_rewrite"] = []

    return state


def get_section_writer(section_name: str, chapter_names: Optional[Dict[str, str]] = None) -> Optional[str]:
    """
    根据章节名称获取对应的写作函数键名
    
    Args:
        section_name: 章节名称
        chapter_names: 可选的章节名称映射字典，如未提供则使用默认值
        
    Returns:
        对应的写作函数键名（如 "write_chapter1"），如果未找到则返回 None
    """
    if chapter_names is None:
        from src.agents.planner import DEFAULT_CHAPTER_NAMES
        chapter_names = DEFAULT_CHAPTER_NAMES
    
    for chapter_key, name in chapter_names.items():
        if section_name == name or section_name.startswith(name):
            return chapter_key
    
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
            if keyword in section_name:
                return chapter_key
    
    return None

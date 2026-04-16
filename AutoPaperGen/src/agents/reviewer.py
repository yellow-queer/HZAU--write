import re
from typing import Dict, Any, List, Set


def extract_all_citations(text: str) -> List[str]:
    cn_pattern = r'（[^）]+\d{4}）'
    en_pattern = r'\([^)]*?\d{4}\)'
    cn_matches = re.findall(cn_pattern, text)
    en_matches = re.findall(en_pattern, text)
    return cn_matches + en_matches


def validate_single_citation(citation_text: str, valid_texts: Set[str]) -> bool:
    return citation_text in valid_texts


def check_citations(state: Dict[str, Any]) -> Dict[str, Any]:
    citation_texts = state.get("citation_texts", {})
    drafts = state.get("drafts", {})
    errors = state.get("errors", [])

    errors = []

    valid_citation_texts = set(citation_texts.values())

    hallucinated_citations: Dict[str, List[str]] = {}

    for section_name, content in drafts.items():
        if not content:
            continue

        citations = extract_all_citations(content)

        invalid_citations = []
        for c in citations:
            if not validate_single_citation(c, valid_citation_texts):
                invalid_citations.append(c)

        if invalid_citations:
            hallucinated_citations[section_name] = invalid_citations
            error_msg = (
                f"章节 '{section_name}' 包含幻觉引文：{', '.join(invalid_citations)}\n"
                f"合法的引文文本: {', '.join(sorted(valid_citation_texts))}"
            )
            errors.append(error_msg)

    state["errors"] = errors

    if errors:
        print(f"发现幻觉引文：{hallucinated_citations}")
        state["sections_to_rewrite"] = list(hallucinated_citations.keys())
    else:
        print("引文检查通过")
        state["sections_to_rewrite"] = []

    return state


def get_section_writer(section_name: str) -> str:
    section_map = {
        "1 绪论": "write_chapter1",
        "2 柑橘多视角图像采集与数据处理": "write_chapter2",
        "3 基于多视角注意力融合的检测模型构建": "write_chapter3",
        "4 实验结果与对比分析": "write_chapter4",
        "5 柑橘实蝇智能检测与问答系统设计与实现": "write_chapter5",
        "6 总结与展望": "write_chapter6"
    }

    return section_map.get(section_name, None)

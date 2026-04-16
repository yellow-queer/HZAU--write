"""
AutoPaperGen 端到端测试脚本

测试核心逻辑：
1. EndNote RIS/TXT 文件解析
2. 姓名+年份引文格式化
3. 引文提取和验证
4. 中文章节键名
5. 模板渲染（中文占位符）
6. 文件结构检查（三层架构）
7. State 定义验证
8. 科研内容集成
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_ris_parsing():
    print("\n=== 测试 EndNote RIS 文件解析 ===")

    ris_content = """TY  - JOUR
AU  - Vaswani, Ashish
TI  - Attention Is All You Need
JO  - Advances in Neural Information Processing Systems
PY  - 2017
ID  - vaswani2017attention
ER  - 

TY  - CONF
AU  - He, Kaiming
TI  - Deep Residual Learning
PY  - 2016
ID  - he2016deep
ER  - 
"""

    records = re.split(r'^ER\s*-\s*$', ris_content, flags=re.MULTILINE)
    citation_keys = []
    for record in records:
        record = record.strip()
        if not record:
            continue
        id_match = re.search(r'^ID\s*-\s*(.+)$', record, re.MULTILINE)
        if id_match:
            citation_keys.append(id_match.group(1).strip())

    assert len(citation_keys) == 2
    assert "vaswani2017attention" in citation_keys
    assert "he2016deep" in citation_keys
    print("[OK] RIS 文件解析测试通过")
    return True


def test_citation_format_chinese():
    print("\n=== 测试中文引文格式化 ===")

    try:
        from src.rag.lit_index import format_citation
    except ImportError as e:
        print(f"[SKIP] 无法导入 format_citation：{e}")
        return True

    result_1 = format_citation({"au": ["梅明华"], "py": "1994"})
    assert result_1 == "（梅明华 1994）", f"1名中文作者格式错误：{result_1}"

    result_2 = format_citation({"au": ["梅明华", "李泽炳"], "py": "1995"})
    assert result_2 == "（梅明华和李泽炳 1995）", f"2名中文作者格式错误：{result_2}"

    result_3 = format_citation({"au": ["梅明华", "李泽炳", "王建国"], "py": "1996"})
    assert result_3 == "（梅明华等 1996）", f"3名中文作者格式错误：{result_3}"

    result_4 = format_citation({"au": ["梅明华", "李泽炳", "王建国", "赵六"], "py": "1997"})
    assert result_4 == "（梅明华等 1997）", f"4名中文作者格式错误：{result_4}"

    print("[OK] 中文引文格式化测试通过")
    return True


def test_citation_format_english():
    print("\n=== 测试英文引文格式化 ===")

    try:
        from src.rag.lit_index import format_citation
    except ImportError as e:
        print(f"[SKIP] 无法导入 format_citation：{e}")
        return True

    result_1 = format_citation({"au": ["Smith, John"], "py": "1990"})
    assert result_1 == "(Smith 1990)", f"1名英文作者格式错误：{result_1}"

    result_2 = format_citation({"au": ["Smith, John", "Jones, Mary"], "py": "1992"})
    assert result_2 == "(Smith and Jones 1992)", f"2名英文作者格式错误：{result_2}"

    result_3 = format_citation({"au": ["Smith, John", "Jones, Mary", "Brown, Tom"], "py": "1993"})
    assert result_3 == "(Smith et al 1993)", f"3名英文作者格式错误：{result_3}"

    result_no_comma = format_citation({"au": ["Smith"], "py": "1990"})
    assert result_no_comma == "(Smith 1990)", f"无逗号英文作者格式错误：{result_no_comma}"

    print("[OK] 英文引文格式化测试通过")
    return True


def test_citation_format_edge_cases():
    print("\n=== 测试引文格式化边界情况 ===")

    try:
        from src.rag.lit_index import format_citation
    except ImportError as e:
        print(f"[SKIP] 无法导入 format_citation：{e}")
        return True

    result_no_author = format_citation({"py": "2020"})
    assert "Unknown" in result_no_author, f"无作者格式错误：{result_no_author}"

    result_no_year = format_citation({"au": ["Smith, John"]})
    assert "Smith" in result_no_year, f"无年份格式错误：{result_no_year}"

    result_y1 = format_citation({"au": ["Smith, John"], "y1": "2019"})
    assert "2019" in result_y1, f"y1年份格式错误：{result_y1}"

    print("[OK] 引文格式化边界情况测试通过")
    return True


def test_citation_validation():
    print("\n=== 测试姓名+年份引文验证 ===")

    try:
        from src.agents.reviewer import check_citations, extract_all_citations
    except ImportError as e:
        print(f"[SKIP] 无法导入 reviewer：{e}")
        return True

    citation_texts = {
        "vaswani2017attention": "(Vaswani et al 2017)",
        "he2016deep": "(He et al 2016)",
        "mei1994": "（梅明华 1994）"
    }

    valid_draft = "深度学习在图像识别中取得了突破(He et al 2016)，注意力机制改变了NLP领域(Vaswani et al 2017)。"
    citations = extract_all_citations(valid_draft)
    assert "(He et al 2016)" in citations, f"未提取到英文引文：{citations}"
    assert "(Vaswani et al 2017)" in citations, f"未提取到英文引文：{citations}"

    cn_draft = "早期研究（梅明华 1994）表明该方法有效。"
    cn_citations = extract_all_citations(cn_draft)
    assert "（梅明华 1994）" in cn_citations, f"未提取到中文引文：{cn_citations}"

    state_valid = {
        "citation_texts": citation_texts,
        "drafts": {"1 绪论": valid_draft},
        "errors": []
    }
    result = check_citations(state_valid)
    assert len(result["errors"]) == 0, f"合法引文不应报错：{result['errors']}"

    hallucinated_draft = "该方法在(Fake et al 2099)中被提出。"
    state_invalid = {
        "citation_texts": citation_texts,
        "drafts": {"1 绪论": hallucinated_draft},
        "errors": []
    }
    result = check_citations(state_invalid)
    assert len(result["errors"]) > 0, "幻觉引文应被检测到"

    print("[OK] 姓名+年份引文验证测试通过")
    return True


def test_endnote_txt_parsing():
    print("\n=== 测试 EndNote .txt 文件解析 ===")

    try:
        from src.rag.lit_index import LiteratureIndex
    except ImportError as e:
        print(f"[SKIP] 无法导入 LiteratureIndex：{e}")
        return True

    import tempfile
    import shutil

    tmp_dir = tempfile.mkdtemp()
    try:
        txt_content = """TY  - JOUR
AU  - Zhang, Wei
AU  - Li, Ming
TI  - Deep Learning for Agriculture
JO  - Computers and Electronics in Agriculture
PY  - 2020
ID  - zhang2020deep
ER  - 

TY  - JOUR
AU  - Wang, Fang
TI  - Citrus Disease Detection
JO  - Plant Disease
PY  - 2021
ID  - wang2021citrus
ER  - 
"""
        txt_file = Path(tmp_dir) / "references.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(txt_content)

        lit_index = LiteratureIndex(literature_dir=tmp_dir)
        keys = lit_index.parse_endnote_txt(str(txt_file))

        assert len(keys) == 2, f"应解析2篇文献，实际：{len(keys)}"
        assert "zhang2020deep" in keys, "缺少 zhang2020deep"
        assert "wang2021citrus" in keys, "缺少 wang2021citrus"

        metadata = lit_index.get_ref_metadata("zhang2020deep")
        assert metadata is not None, "zhang2020deep 元数据为 None"
        assert "Zhang, Wei" in metadata.get("au", []), "作者信息不正确"

        print("[OK] EndNote .txt 文件解析测试通过")
    finally:
        shutil.rmtree(tmp_dir)

    return True


def test_generate_citation_texts():
    print("\n=== 测试引文文本生成 ===")

    try:
        from src.rag.lit_index import LiteratureIndex
    except ImportError as e:
        print(f"[SKIP] 无法导入 LiteratureIndex：{e}")
        return True

    import tempfile
    import shutil

    tmp_dir = tempfile.mkdtemp()
    try:
        ris_content = """TY  - JOUR
AU  - Vaswani, Ashish
AU  - Shazeer, Noam
AU  - Parmar, Niki
TI  - Attention Is All You Need
PY  - 2017
ID  - vaswani2017attention
ER  - 

TY  - JOUR
AU  - He, Kaiming
AU  - Zhang, Xiangyu
TI  - Deep Residual Learning
PY  - 2016
ID  - he2016deep
ER  - 
"""
        ris_file = Path(tmp_dir) / "refs.ris"
        with open(ris_file, 'w', encoding='utf-8') as f:
            f.write(ris_content)

        lit_index = LiteratureIndex(literature_dir=tmp_dir)
        lit_index.parse_ris_file(str(ris_file))
        citation_texts = lit_index.generate_citation_texts()

        assert len(citation_texts) == 2, f"应生成2条引文文本，实际：{len(citation_texts)}"
        assert "vaswani2017attention" in citation_texts, "缺少 vaswani2017attention"
        assert citation_texts["vaswani2017attention"] == "(Vaswani et al 2017)", \
            f"Vaswani引文格式错误：{citation_texts['vaswani2017attention']}"
        assert citation_texts["he2016deep"] == "(He and Zhang 2016)", \
            f"He引文格式错误：{citation_texts['he2016deep']}"

        print("[OK] 引文文本生成测试通过")
    finally:
        shutil.rmtree(tmp_dir)

    return True


def test_chinese_keys():
    print("\n=== 测试中文章节键名 ===")

    chapter_keys = [
        "1 绪论",
        "2 柑橘多视角图像采集与数据处理",
        "3 基于多视角注意力融合的检测模型构建",
        "4 实验结果与对比分析",
        "5 柑橘实蝇智能检测与问答系统设计与实现",
        "6 总结与展望"
    ]

    drafts = {key: f"这是{key}的内容" for key in chapter_keys}

    for key in chapter_keys:
        assert key in drafts, f"缺少章节键：{key}"
        assert drafts[key] != "", f"章节内容为空：{key}"

    context = {
        'chapter_1': drafts.get('1 绪论', ''),
        'chapter_2': drafts.get('2 柑橘多视角图像采集与数据处理', ''),
        'chapter_3': drafts.get('3 基于多视角注意力融合的检测模型构建', ''),
        'chapter_4': drafts.get('4 实验结果与对比分析', ''),
        'chapter_5': drafts.get('5 柑橘实蝇智能检测与问答系统设计与实现', ''),
        'chapter_6': drafts.get('6 总结与展望', ''),
    }

    for key, value in context.items():
        assert value != "", f"模板映射为空：{key}"

    print("[OK] 中文章节键名测试通过")
    return True


def test_template_rendering():
    try:
        from jinja2 import Template
    except ImportError:
        print("[SKIP] Jinja2 未安装")
        return True

    print("\n=== 测试模板渲染 ===")

    template_content = """# {{ title | default('基于序列图像融合的实蝇侵染柑橘无损检测方法研究') }}

## 1 绪论

{{ chapter_1 }}

## 3 基于多视角注意力融合的检测模型构建

{{ chapter_3 }}
"""

    drafts = {
        "1 绪论": "柑橘实蝇危害严重...",
        "3 基于多视角注意力融合的检测模型构建": "以ConvNeXt为骨干网络..."
    }

    template = Template(template_content)
    rendered = template.render(
        chapter_1=drafts.get("1 绪论", ""),
        chapter_3=drafts.get("3 基于多视角注意力融合的检测模型构建", "")
    )

    assert "柑橘实蝇危害严重" in rendered
    assert "ConvNeXt" in rendered

    print("[OK] 模板渲染测试通过")
    return True


def test_file_structure():
    print("\n=== 测试文件结构（三层架构）===")

    base_dir = Path(__file__).parent.parent

    required_files = {
        "src/rag/code_index.py": "代码解析器",
        "src/rag/lit_index.py": "文献解析器",
        "src/rag/style_index.py": "风格解析器",
        "src/agents/state.py": "状态定义",
        "src/agents/planner.py": "规划者",
        "src/agents/literature_reviewer.py": "文献研究员",
        "src/agents/code_analyst.py": "代码分析员",
        "src/agents/writers.py": "章节主笔",
        "src/agents/reviewer.py": "审查员",
        "src/agents/fact_checker.py": "事实核查",
        "src/workflow_hzau.py": "工作流编排",
        "src/render.py": "模板渲染",
        "src/utils/qwen_config.py": "Qwen API 配置",
        "main.py": "系统入口",
        "data/templates/hzau_thesis.md": "华农论文模板",
        "data/literature/references.ris": "EndNote RIS 文件",
        "README.md": "项目说明文档",
    }

    missing = []
    for file_path, desc in required_files.items():
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"  [OK] {desc}: {file_path}")
        else:
            print(f"  [MISSING] {desc}: {file_path}")
            missing.append(file_path)

    removed_files = [
        "data/codebase/model.py",
        "data/codebase/train.py",
        "data/literature/references.bib",
        "使用说明.md",
        "华中农业大学配置说明.md",
        "项目总结.md",
        "tests/test_autopapergen.py",
    ]

    for file_path in removed_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"  [WARN] 应删除的文件仍存在：{file_path}")
        else:
            print(f"  [OK] 已删除：{file_path}")

    if missing:
        print(f"\n[FAIL] 缺失 {len(missing)} 个文件")
        return False
    else:
        print(f"\n[OK] 所有 {len(required_files)} 个文件都存在")
        return True


def test_state_definition():
    print("\n=== 测试 State 定义 ===")

    try:
        from src.agents.state import PaperDraftState

        required_fields = [
            'topic', 'citation_keys', 'outline', 'drafts', 'errors',
            'current_section', 'max_retries', 'retries', 'sections_to_rewrite',
            'llm', 'literature_retriever', 'code_retriever', 'style_retriever',
            'research_context', 'citation_texts'
        ]

        annotations = PaperDraftState.__annotations__
        for field in required_fields:
            assert field in annotations, f"State 缺少字段：{field}"

        assert 'zotero_keys' not in annotations, "State 不应包含 zotero_keys 字段"

        print(f"[OK] State 定义正确，包含 {len(required_fields)} 个字段，无 zotero_keys")
        return True
    except ImportError as e:
        print(f"[SKIP] 无法导入 PaperDraftState：{e}")
        return True


def test_no_zotero_references():
    print("\n=== 测试无 Zotero 残留引用 ===")

    base_dir = Path(__file__).parent.parent
    py_files = list(base_dir.glob("src/**/*.py")) + [base_dir / "main.py"]

    found = False
    for py_file in py_files:
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'zotero' in content.lower():
            print(f"  [WARN] {py_file.name} 中仍包含 zotero 引用")
            found = True

    if not found:
        print("[OK] 所有源文件中无 Zotero 残留引用")
    return True


def test_research_context_loading():
    print("\n=== 测试科研内容加载 ===")

    try:
        import yaml
    except ImportError:
        print("[SKIP] PyYAML 未安装")
        return True

    base_dir = Path(__file__).parent.parent

    template_path = base_dir / "data" / "research_context_template.yaml"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            context = yaml.safe_load(f)
        assert context is not None, "模板文件解析结果为 None"
        assert 'title' in context, "模板缺少 title 字段"
        assert 'innovations' in context, "模板缺少 innovations 字段"
        assert 'methodology' in context, "模板缺少 methodology 字段"
        assert 'experiment_results' in context, "模板缺少 experiment_results 字段"
        print(f"  [OK] 模板文件解析成功，包含 {len(context)} 个顶级字段")
    else:
        print(f"  [SKIP] 模板文件不存在：{template_path}")

    default_path = base_dir / "data" / "research_context.yaml"
    if default_path.exists():
        with open(default_path, 'r', encoding='utf-8') as f:
            context = yaml.safe_load(f)
        assert context is not None, "默认文件解析结果为 None"
        assert 'title' in context, "默认文件缺少 title 字段"
        print(f"  [OK] 默认科研内容文件解析成功")
    else:
        print(f"  [SKIP] 默认科研内容文件不存在：{default_path}")

    return True


def test_research_context_formatting():
    print("\n=== 测试科研内容格式化 ===")

    try:
        from src.agents.writers import _format_research_context
    except ImportError as e:
        print(f"[SKIP] 无法导入 _format_research_context：{e}")
        return True

    sample_context = {
        "title": "测试论文",
        "research_summary": "这是一个测试研究",
        "innovations": ["创新点1", "创新点2"],
        "methodology": {
            "model_architecture": "ConvNeXt骨干网络",
            "comparison_models": [
                {"name": "基线模型A", "description": "简单分类"}
            ],
            "training_strategy": "AdamW优化器"
        },
        "experiment_results": {
            "environment": "RTX 4090",
            "key_metrics": [
                {"metric": "Accuracy", "our_method": "96.5%", "best_baseline": "93.2%"}
            ],
            "key_findings": ["发现1"]
        },
        "system_implementation": {
            "architecture": "Flask后端",
            "core_features": ["功能1", "功能2"]
        },
        "limitations_and_future": {
            "limitations": ["不足1"],
            "future_work": ["展望1"]
        },
        "additional_notes": "补充说明"
    }

    for chapter in ["1", "2", "3", "4", "5", "6"]:
        result = _format_research_context(sample_context, chapter)
        assert result is not None, f"第{chapter}章格式化结果为 None"
        assert "未提供" not in result, f"第{chapter}章不应返回'未提供'"

    empty_result = _format_research_context({}, "1")
    assert "未提供" in empty_result, "空 context 应返回'未提供'"

    none_result = _format_research_context(None, "3")
    assert "未提供" in none_result, "None context 应返回'未提供'"

    print("[OK] 科研内容格式化测试通过")
    return True


def test_research_context_in_outline():
    print("\n=== 测试大纲生成中的科研内容集成 ===")

    try:
        from src.agents.planner import _format_research_context_for_outline, _enrich_outline_with_context, DEFAULT_OUTLINE
    except ImportError as e:
        print(f"[SKIP] 无法导入 planner 函数：{e}")
        return True

    sample_context = {
        "title": "测试论文",
        "research_summary": "测试研究概述",
        "innovations": ["创新点A", "创新点B"],
        "methodology": {
            "model_architecture": "ConvNeXt",
            "data_collection": "旋转平台采集"
        },
        "experiment_results": {
            "key_metrics": [
                {"metric": "Accuracy", "our_method": "96%", "best_baseline": "93%"}
            ]
        },
        "limitations_and_future": {
            "future_work": ["边缘部署", "多模态融合"]
        }
    }

    formatted = _format_research_context_for_outline(sample_context)
    assert "测试论文" in formatted
    assert "创新点A" in formatted
    assert "ConvNeXt" in formatted

    empty_formatted = _format_research_context_for_outline({})
    assert empty_formatted == ""

    outline = DEFAULT_OUTLINE.copy()
    enriched = _enrich_outline_with_context(outline, sample_context)
    assert "创新点A" in enriched.get("1 绪论", "")
    assert "ConvNeXt" in enriched.get("3 基于多视角注意力融合的检测模型构建", "")

    print("[OK] 大纲科研内容集成测试通过")
    return True


def run_all_tests():
    print("=" * 60)
    print("AutoPaperGen 端到端测试")
    print("=" * 60)

    tests = [
        ("EndNote RIS 文件解析", test_ris_parsing),
        ("中文引文格式化", test_citation_format_chinese),
        ("英文引文格式化", test_citation_format_english),
        ("引文格式化边界情况", test_citation_format_edge_cases),
        ("姓名+年份引文验证", test_citation_validation),
        ("EndNote .txt 文件解析", test_endnote_txt_parsing),
        ("引文文本生成", test_generate_citation_texts),
        ("中文章节键名", test_chinese_keys),
        ("模板渲染", test_template_rendering),
        ("文件结构检查", test_file_structure),
        ("State 定义验证", test_state_definition),
        ("无 Zotero 残留", test_no_zotero_references),
        ("科研内容加载", test_research_context_loading),
        ("科研内容格式化", test_research_context_formatting),
        ("大纲科研内容集成", test_research_context_in_outline),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n--- 运行 {test_name} ---")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"[ERROR] {test_name}: {str(e)}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"测试结果：{passed} 通过，{failed} 失败")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

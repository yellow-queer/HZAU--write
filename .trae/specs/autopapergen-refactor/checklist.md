# AutoPaperGen 架构重构验收检查清单

## P0 致命 Bug 修复
- [x] main.py 导入路径正确（from src.workflow_hzau import create_workflow）
- [x] workflow_hzau.py 变量名正确（citation_keys 而非 zotero_keys）
- [x] writer 函数能从 state 中获取 LLM 和检索器
- [x] drafts 键名使用中文（"1 绪论" 而非 "Methodology"）
- [x] 运行 `python main.py` 不报 ModuleNotFoundError

## 三层架构
- [x] 数据与索引层：代码解析器 (CodeSplitter) → Code Vector DB
- [x] 数据与索引层：文献解析器 (RIS/PDF) → Literature Vector DB
- [x] 数据与索引层：风格解析器 (SentenceSplitter) → Style Vector DB
- [x] Agent 编排层：State 包含提纲、各章草稿、引文列表
- [x] Agent 编排层：规划者 (Outline Planner) 正常工作
- [x] Agent 编排层：文献研究员 (Literature Reviewer) 正常工作
- [x] Agent 编排层：代码分析员 (Code Analyst) 正常工作
- [x] Agent 编排层：章节主笔 (Section Writers) 按章节独立撰写
- [x] Agent 编排层：审查员 (Reviewer & Citation Checker) 正常工作
- [x] 验证层：事实核查 (Fact-Checking against Code) 正常工作
- [x] 验证层：引文校验 (Citation Grounding) 正常工作

## 分章节撰写
- [x] 第 1 章 绪论：使用文献库 RAG，正确引用
- [x] 第 2 章 数据采集：使用代码库 RAG，描述与代码一致
- [x] 第 3 章 模型构建：使用代码库 RAG，描述与代码一致
- [x] 第 4 章 实验分析：使用代码库 RAG，描述与代码一致
- [x] 第 5 章 系统实现：使用代码库 RAG，描述与代码一致
- [x] 第 6 章 总结展望：综合使用

## 引用格式
- [x] 所有 \cite{} 引用来自 EndNote RIS 文件中的 citation_keys
- [x] Review 节点能检测幻觉引文并打回重写
- [x] 引文格式为 \cite{key}

## 冗余代码清理
- [x] state.py 中无 zotero_keys 字段
- [x] lit_index.py 中无 zotero_keys/bib_metadata 兼容属性
- [x] qwen_config.py 中无未使用的导入
- [x] data/codebase/ 中无旧版示例文件
- [x] data/literature/ 中无重复的 .bib 文件

## 输出格式
- [x] 输出为符合华中农业大学论文模板格式的可编辑 Markdown 文档
- [x] 模板渲染使用中文章节键名
- [x] 输出文件保存在 output/ 目录

## Embedding 接口
- [x] Embedding 模型使用 LlamaIndex 兼容接口
- [x] lit_index.py 和 code_index.py 的 build_index() 能正确接收嵌入模型

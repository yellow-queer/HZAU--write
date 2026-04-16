# AutoPaperGen 学术论文初稿自动生成系统 Spec

## Why
研究人员需要花费大量时间撰写学术论文初稿，特别是在整理代码实现细节、文献综述和格式化排版方面。本系统旨在通过多 Agent 协作和 RAG 技术，基于给定的研究主题、项目代码库和参考文献库，自动生成符合指定模板格式的论文初稿，大幅减少重复性写作工作。

## What Changes
- **新增** 完整的多 Agent 学术论文生成系统
- **新增** 双知识库 RAG 架构（代码库 + 文献库独立检索）
- **新增** Zotero 文献引用解析与验证机制
- **新增** LangGraph 状态机编排的工作流引擎
- **新增** Jinja2 模板渲染系统
- **新增** 引文幻觉检测与自动修正机制

## Impact
- **技术栈**: LangGraph (状态机编排), LlamaIndex (RAG), Pydantic (数据验证), Jinja2 (模板渲染), ChromaDB/FAISS (向量库)
- **目录结构**: 严格分离数据源 (codebase/literature/templates)
- **核心约束**: 
  - 代码库 RAG 仅供 Method/Experiment 章节使用
  - 文献库 RAG 仅供 Related Work/Intro 章节使用
  - 所有引文必须来自 Zotero .bib 文件，严禁幻觉

## ADDED Requirements

### Requirement: 双知识库 RAG 系统
系统 SHALL 为代码库和文献库建立完全独立的检索管道：
- **代码知识库**: 使用 LlamaIndex CodeSplitter 进行 AST 感知的代码切分
- **文献知识库**: 解析 PDF 和 .bib 文件，提取元数据

#### Scenario: 初始化 RAG 检索器
- **WHEN** 系统启动时
- **THEN** 分别加载 `data/codebase/` 和 `data/literature/` 目录，创建独立的向量索引

### Requirement: Zotero 文献引用标准
系统 SHALL 解析 `data/literature/` 目录下的 .bib 文件，提取所有 Citation Keys 和元数据。

#### Scenario: 引文验证
- **WHEN** Agent 撰写需要引用的内容时
- **THEN** 必须且只能使用 .bib 文件中存在的 Key，格式为 `\cite{key}`
- **AND** Review 节点会验证所有引文，发现幻觉引文则打回重写

### Requirement: 模板渲染引擎
系统 SHALL 使用 Jinja2 读取 `data/templates/` 中的模板文件，将各章节草稿注入模板。

#### Scenario: 渲染输出
- **WHEN** 所有章节撰写完成且通过引文审查
- **THEN** 读取模板文件，将 state.drafts 中的内容注入 `{{ section_name }}` 占位符
- **AND** 输出到 `output/` 目录

### Requirement: 多 Agent 状态机 (LangGraph)
系统 SHALL 使用 LangGraph 定义以下节点：
1. **Init**: 初始化 RAG 检索器，解析 .bib 文件
2. **Plan_Outline**: 生成论文大纲
3. **Write_Method**: 仅查询 Codebase RAG
4. **Write_RelatedWork**: 仅查询 Literature RAG，强制使用 Zotero Keys
5. **Review_Citations**: 验证引文，条件边打回重写
6. **Render_Output**: 渲染模板并保存

#### State 定义
- `topic`: str - 研究主题
- `zotero_keys`: List[str] - 合法引文 Keys
- `outline`: Dict[str, Any] - 论文大纲
- `drafts`: Dict[str, str] - 各章节草稿
- `errors`: List[str] - 错误列表

## MODIFIED Requirements
无（全新系统）

## REMOVED Requirements
无（全新系统）

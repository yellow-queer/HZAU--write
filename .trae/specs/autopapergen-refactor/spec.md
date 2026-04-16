# AutoPaperGen 架构重构与功能补全 Spec

## Why
当前代码存在多个致命 Bug（workflow 导入路径错误、writer 无法接收 LLM、drafts 键名不匹配），且架构与目标三层设计（数据索引层 / Agent 编排层 / 验证对齐层）差距较大。需要重构代码结构、修复 Bug、补全缺失功能，使系统能够分章节完成论文书写并正确引用。

## What Changes
- **修复** main.py 导入路径（workflow.py 不存在 → workflow_hzau.py）
- **修复** writer 函数无法接收 LLM 和检索器的致命 Bug
- **修复** drafts 键名不匹配（英文键 → 中文章节名键）
- **重构** 项目结构为三层架构（数据索引层 / Agent 编排层 / 验证对齐层）
- **新增** 风格解析器 (Style Vector DB)
- **新增** 文献研究员 Agent (Literature Reviewer)
- **新增** 代码分析员 Agent (Code Analyst)
- **新增** 事实核查 (Fact-Checking against Code)
- **重构** 章节主笔为并行执行
- **删除** 冗余代码（zotero_keys 兼容层、旧版示例文件、未使用导入）
- **统一** Embedding 模型接口（LangChain → LlamaIndex）

## Impact
- **受影响文件**: main.py, src/workflow*.py, src/agents/*.py, src/rag/*.py, src/render.py, src/utils/qwen_config.py
- **删除文件**: src/workflow.py（如存在旧版）, data/codebase/model.py（旧版示例）, data/codebase/train.py（旧版示例）, data/literature/references.bib（与 RIS 重复）
- **新增文件**: src/rag/style_index.py, src/agents/literature_reviewer.py, src/agents/code_analyst.py, src/agents/fact_checker.py

## ADDED Requirements

### Requirement: 三层架构
系统 SHALL 按以下三层架构组织：

**数据与索引层 (Ingestion & Indexing) - LlamaIndex**：
- 代码解析器 (AST / CodeSplitter) → Code Vector DB
- 文献解析器 (Nougat / Marker) → Literature Vector DB
- 风格解析器 (SentenceSplitter) → Style Vector DB

**多 Agent 编排层 (Orchestration) - LangGraph**：
- State: PaperDraftState (全局状态：提纲、各章草稿、引文列表)
- Agent 1: 规划者 (Outline Planner)
- Agent 2: 文献研究员 (Literature Reviewer)
- Agent 3: 代码分析员 (Code Analyst)
- Agent 4: 章节主笔 (Section Writers - 并行执行)
- Agent 5: 审查员 (Reviewer & Citation Checker)

**验证与对齐层 (Verification)**：
- 事实核查 (Fact-Checking against Code)
- 引文校验 (Citation Grounding & Anti-Hallucination)

#### Scenario: 完整运行流程
- **WHEN** 用户运行 `python main.py "研究主题" data/templates/hzau_thesis.md`
- **THEN** 系统依次执行：初始化索引 → 生成大纲 → 分章节撰写（并行）→ 引文校验 → 事实核查 → 渲染输出
- **AND** 输出为符合华中农业大学论文模板格式的可编辑文档

### Requirement: 分章节撰写
系统 SHALL 支持按 6 章结构分章节撰写论文，每章使用专属的 writer 函数和 Prompt。

#### Scenario: 章节撰写
- **WHEN** 工作流执行到章节撰写阶段
- **THEN** 每个章节使用对应的 writer 函数
- **AND** writer 从 state 中获取 LLM 和检索器
- **AND** drafts 使用中文键名（如 "1 绪论", "3 基于多视角注意力融合的检测模型构建"）

### Requirement: 风格解析器
系统 SHALL 提供风格解析器，使用 SentenceSplitter 构建风格向量库，用于保持论文写作风格一致性。

### Requirement: 文献研究员 Agent
系统 SHALL 提供文献研究员 Agent，负责从文献库中提取关键信息、总结研究现状，为章节主笔提供文献素材。

### Requirement: 代码分析员 Agent
系统 SHALL 提供代码分析员 Agent，负责从代码库中提取架构、算法、实验参数等信息，为方法章节和实验章节提供素材。

### Requirement: 事实核查
系统 SHALL 在引文校验之外，增加事实核查功能，验证章节内容中关于代码的描述是否与实际代码一致。

## MODIFIED Requirements

### Requirement: Writer 函数参数传递
Writer 函数 SHALL 从 state 中获取 LLM 和检索器，而非通过函数参数传递。LLM 和检索器在 init 阶段存入 state。

### Requirement: 统一键名体系
所有 drafts 键名 SHALL 使用中文章节名，与华农模板占位符一致。

### Requirement: Embedding 模型接口
Embedding 模型 SHALL 使用 LlamaIndex 兼容接口，通过 `Settings.embed_model` 设置。

## REMOVED Requirements

### Requirement: zotero_keys 兼容字段
**Reason**: 已全面迁移至 EndNote RIS，不再需要 Zotero 兼容
**Migration**: 所有 `zotero_keys` 引用替换为 `citation_keys`

### Requirement: 旧版 workflow.py
**Reason**: 已被 workflow_hzau.py 替代
**Migration**: 删除旧文件，main.py 直接导入 workflow_hzau

### Requirement: 旧版示例代码 (data/codebase/model.py, train.py)
**Reason**: 与实际项目代码无关，是初始搭建时的占位文件
**Migration**: 删除文件

# 引文格式改造与项目清理 Spec

## Why

当前系统存在三个核心问题：
1. **引文格式不符合华中农业大学论文要求**：系统使用 `\cite{key}` 格式（LaTeX 风格），但学校要求使用"姓名+年份"格式，如"（梅明华 1994）"、"(Smith et al 1993)"
2. **文献解析仅支持 .ris 文件**：用户使用 EndNote 管理文献，EndNote 可导出 .txt 格式（标签式），当前系统只解析 .ris 文件
3. **项目存在大量冗余/过时文件**：使用说明.md、华中农业大学配置说明.md、项目总结.md 内容严重过时（仍提及 Zotero/.bib），test_autopapergen.py 使用旧版 API（parse_bib_file、get_bib_metadata），缺少 README.md

## What Changes

- **BREAKING**: 引文格式从 `\cite{key}` 改为"姓名+年份"格式
- 新增 EndNote .txt 文件解析支持（与 .ris 并行）
- 新增引文格式化引擎：根据作者数量自动生成"（作者 年份）"格式
- 更新 reviewer.py 引文校验逻辑：校验"姓名+年份"格式而非 `\cite{}`
- 更新 writers.py 所有 prompt：指示 LLM 使用新引文格式
- 删除过时文档（使用说明.md、华中农业大学配置说明.md、项目总结.md）
- 删除过时测试文件（test_autopapergen.py）
- 创建 README.md 替代所有旧文档

## Impact

- Affected code: `src/rag/lit_index.py`, `src/agents/reviewer.py`, `src/agents/writers.py`, `src/agents/state.py`, `src/render.py`
- Affected data: `data/literature/` 需同时支持 .ris 和 .txt
- Affected tests: `tests/test_core.py`, 删除 `tests/test_autopapergen.py`
- Affected docs: 删除 3 个旧 .md，新建 README.md

## ADDED Requirements

### Requirement: 姓名+年份引文格式

系统 SHALL 在生成的论文中使用"姓名+年份"引文格式，遵循华中农业大学论文规范：

#### Scenario: 中文文献1名作者
- **WHEN** 引用的文献只有1名中文作者
- **THEN** 格式为"（姓名 年份）"，如"（梅明华 1994）"

#### Scenario: 中文文献2名作者
- **WHEN** 引用的文献有2名中文作者
- **THEN** 格式为"（姓名1和姓名2 年份）"，如"（梅明华和李泽炳 1995）"

#### Scenario: 中文文献3名及以上作者
- **WHEN** 引用的文献有3名或以上中文作者
- **THEN** 格式为"（第一作者等 年份）"，如"（梅明华等 1996）"

#### Scenario: 英文文献1名作者
- **WHEN** 引用的文献只有1名英文作者
- **THEN** 格式为"(Surname Year)"，如"(Smith 1990)"

#### Scenario: 英文文献2名作者
- **WHEN** 引用的文献有2名英文作者
- **THEN** 格式为"(Surname1 and Surname2 Year)"，如"(Smith and Jones 1992)"

#### Scenario: 英文文献3名及以上作者
- **WHEN** 引用的文献有3名或以上英文作者
- **THEN** 格式为"(FirstSurname et al Year)"，如"(Smith et al 1993)"

#### Scenario: 同一括弧多篇文献
- **WHEN** 一个括弧中引用多篇文献
- **THEN** 按年代顺序排列，早期在前，文献间用逗号分隔，如"(Smith 1990, Vaswani 2017)"

### Requirement: EndNote .txt 文件解析

系统 SHALL 支持解析 EndNote 导出的 .txt 文件（标签式格式），与 .ris 文件并行支持。

#### Scenario: 自动检测文献文件格式
- **WHEN** `data/literature/` 目录中存在 .txt 或 .ris 文件
- **THEN** 系统自动识别文件格式并使用对应解析器

#### Scenario: 解析 EndNote .txt 文件
- **WHEN** 用户提供 EndNote 导出的 .txt 文件
- **THEN** 系统提取作者(AU)、标题(TI)、年份(PY)、期刊(JO)等元数据，与 .ris 解析结果格式一致

### Requirement: 引文格式化引擎

系统 SHALL 提供引文格式化功能，根据文献元数据自动生成"姓名+年份"格式的引文文本。

#### Scenario: 格式化单条引文
- **WHEN** 给定一条文献的元数据（作者列表、年份）
- **THEN** 根据作者数量和语言自动生成正确格式的引文文本

#### Scenario: 生成可用引文列表
- **WHEN** 系统解析完所有文献后
- **THEN** 为每条文献生成格式化引文文本，供 LLM 在写作时使用

### Requirement: README.md

系统 SHALL 提供一份准确的 README.md 文件，反映当前项目状态。

#### Scenario: README 内容准确性
- **WHEN** 用户阅读 README.md
- **THEN** 文档正确描述 EndNote 文献管理、姓名+年份引文格式、三层架构、research_context 功能

## MODIFIED Requirements

### Requirement: 引文校验

原要求：校验 `\cite{key}` 格式，验证 key 在 citation_keys 列表中。
新要求：校验"姓名+年份"格式，验证引用的文献在已知文献列表中。校验方式改为检查括弧内的引文文本是否匹配已知文献的格式化引文。

### Requirement: Writer Prompts

原要求：指示 LLM 使用 `\cite{key}` 格式引用。
新要求：指示 LLM 使用"姓名+年份"格式引用，并提供可用引文文本列表（如"（梅明华 1994）"、"(Vaswani et al 2017)"）。

## REMOVED Requirements

### Requirement: \cite{} 引文格式
**Reason**: 不符合华中农业大学论文格式要求
**Migration**: 所有 `\cite{key}` 引用替换为"姓名+年份"格式

### Requirement: 旧版文档文件
**Reason**: 使用说明.md、华中农业大学配置说明.md、项目总结.md 内容严重过时，仍提及 Zotero/.bib，与当前代码不一致
**Migration**: 合并为一份准确的 README.md

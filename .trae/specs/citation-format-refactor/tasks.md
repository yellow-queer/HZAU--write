# Tasks

- [x] **Task 1**: 实现引文格式化引擎
  - [x] 在 `src/rag/lit_index.py` 中添加 `format_citation()` 函数
  - [x] 在 `src/rag/lit_index.py` 中添加 `generate_citation_texts()` 方法
  - [x] 在 `src/agents/state.py` 中添加 `citation_texts: Dict[str, str]` 字段

- [x] **Task 2**: 支持 EndNote .txt 文件解析
  - [x] 在 `src/rag/lit_index.py` 中添加 `parse_endnote_txt()` 方法
  - [x] 添加 `parse_literature_files()` 统一入口：自动检测 .ris 和 .txt 文件
  - [x] .txt 和 .ris 解析结果格式一致（统一存入 ref_metadata）

- [x] **Task 3**: 更新引文校验逻辑
  - [x] 修改 `src/agents/reviewer.py`：将 `\cite{key}` 正则替换为"姓名+年份"格式检测
  - [x] 校验逻辑：检查文本中括弧引文是否匹配 citation_texts 中的已知格式化文本
  - [x] 更新 `extract_all_citations()` 函数

- [x] **Task 4**: 更新 Writer Prompts
  - [x] 修改 CHAPTER1 和 CHAPTER6 的 prompt：将 `\cite{key}` 指令替换为"姓名+年份"格式指令
  - [x] 在 prompt 中注入可用引文文本列表
  - [x] 更新 CHAPTER1 的 citation_keys 占位符为 citation_texts

- [x] **Task 5**: 更新 render.py 和 main.py
  - [x] 更新 `main.py`：调用 `generate_citation_texts()` 并将 citation_texts 放入 initial_state
  - [x] 更新 `render.py`：添加 `_generate_references_list()` 函数和 references_list 渲染字段

- [x] **Task 6**: 删除冗余文件并创建 README.md
  - [x] 删除 `使用说明.md`
  - [x] 删除 `华中农业大学配置说明.md`
  - [x] 删除 `项目总结.md`
  - [x] 删除 `tests/test_autopapergen.py`
  - [x] 创建 `README.md`

- [x] **Task 7**: 更新测试
  - [x] 更新 `tests/test_core.py`：将 `\cite{key}` 相关测试替换为"姓名+年份"格式测试
  - [x] 添加引文格式化测试：验证1/2/3+作者的中文和英文格式
  - [x] 添加 EndNote .txt 解析测试
  - [x] 更新引文校验测试：验证新格式的幻觉检测

# Task Dependencies
- Task 2 依赖于 Task 1（.txt 解析需要复用引文格式化引擎）
- Task 3 依赖于 Task 1（校验需要知道格式化引文文本）
- Task 4 依赖于 Task 1 和 Task 3（prompt 需要新格式指令和可用引文列表）
- Task 5 依赖于 Task 1 和 Task 4（main.py 需要调用新方法）
- Task 6 无依赖，可并行执行
- Task 7 依赖于所有其他任务

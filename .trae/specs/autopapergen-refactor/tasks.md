# AutoPaperGen 架构重构任务清单

## Tasks

- [x] **Task 1**: 修复致命 Bug（P0）
  - [x] 修复 main.py 导入路径：`from src.workflow import create_workflow` → `from src.workflow_hzau import create_workflow`
  - [x] 修复 workflow_hzau.py 第 67 行变量名错误：`len(zotero_keys)` → `len(citation_keys)`
  - [x] 修复 writer 函数参数传递：将 LLM 和检索器存入 state，writer 从 state 读取
  - [x] 统一 drafts 键名为中文章节名

- [x] **Task 2**: 重构项目结构为三层架构
  - [x] 创建 src/rag/style_index.py：风格解析器（SentenceSplitter → Style Vector DB）
  - [x] 创建 src/agents/literature_reviewer.py：文献研究员 Agent
  - [x] 创建 src/agents/code_analyst.py：代码分析员 Agent
  - [x] 创建 src/agents/fact_checker.py：事实核查 Agent
  - [x] 重构 workflow_hzau.py：按三层架构重新编排节点

- [x] **Task 3**: 为 6 章创建独立 writer 函数
  - [x] 创建 write_chapter1()：绪论（使用文献库 RAG）
  - [x] 创建 write_chapter2()：数据采集与处理（使用代码库 RAG）
  - [x] 创建 write_chapter3()：模型构建（使用代码库 RAG）
  - [x] 创建 write_chapter4()：实验分析（使用代码库 RAG）
  - [x] 创建 write_chapter5()：系统实现（使用代码库 RAG）
  - [x] 创建 write_chapter6()：总结展望（综合使用）

- [x] **Task 4**: 清理冗余代码
  - [x] 删除 state.py 中的 zotero_keys 字段
  - [x] 删除 lit_index.py 中的 zotero_keys/bib_metadata 兼容属性和方法
  - [x] 删除 qwen_config.py 中未使用的导入
  - [x] 删除 data/codebase/model.py（旧版示例）
  - [x] 删除 data/codebase/train.py（旧版示例）
  - [x] 删除 data/literature/references.bib（与 RIS 重复）
  - [x] 统一 Embedding 模型接口为 LlamaIndex 兼容

- [x] **Task 5**: 更新 render.py 和模板
  - [x] 确保渲染上下文使用中文章节键名
  - [x] 删除英文键名映射（abstract, introduction 等）
  - [x] 确保输出为可编辑的 Markdown 文档

- [x] **Task 6**: 端到端测试
  - [x] 验证 RIS 解析正确
  - [x] 验证 Qwen API 调用正常
  - [x] 验证分章节撰写流程
  - [x] 验证引文校验功能
  - [x] 验证模板渲染输出

## Task Dependencies
- Task 2 依赖于 Task 1（先修复 Bug 再重构）
- Task 3 依赖于 Task 1（writer 需要新的参数传递机制）
- Task 4 依赖于 Task 1 和 Task 3（清理前需确保功能正常）
- Task 5 依赖于 Task 3（模板需要配合新键名）
- Task 6 依赖于所有其他任务

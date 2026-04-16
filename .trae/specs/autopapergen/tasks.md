# AutoPaperGen 开发任务清单

## Tasks

- [x] **Task 1**: 生成 requirements.txt 并搭建基础目录结构
  - [x] 创建 requirements.txt，包含 langgraph, llama-index, pydantic, jinja2, chromadb 等依赖
  - [x] 创建 data/codebase/, data/literature/, data/templates/ 目录
  - [x] 创建 src/rag/, src/agents/ 目录
  - [x] 创建 output/ 目录
  - [x] 创建 main.py 入口文件框架

- [x] **Task 2**: 实现双知识库 RAG 构建逻辑
  - [x] 编写 src/rag/lit_index.py: 解析 .bib 文件，提取 Citation Keys 和元数据
  - [x] 编写 src/rag/lit_index.py: 为文献 PDF 创建 LlamaIndex 向量索引
  - [x] 编写 src/rag/code_index.py: 使用 CodeSplitter 切分代码库
  - [x] 编写 src/rag/code_index.py: 为代码创建 LlamaIndex 向量索引
  - [x] 确保两个索引完全独立，提供统一的检索接口

- [x] **Task 3**: 实现 LangGraph 状态定义和 Agent 节点逻辑
  - [x] 编写 src/agents/state.py: 定义 TypedDict 状态（topic, zotero_keys, outline, drafts, errors）
  - [x] 编写 src/agents/planner.py: 实现提纲生成 Agent，根据 topic 生成论文章节结构
  - [x] 编写 src/agents/writers.py: 实现 Method Writer，仅查询 Codebase RAG
  - [x] 编写 src/agents/writers.py: 实现 RelatedWork Writer，仅查询 Literature RAG，强制使用 Zotero Keys
  - [x] 编写 src/agents/reviewer.py: 实现引文审查 Agent，用正则检查 \cite{} 是否在 zotero_keys 中

- [x] **Task 4**: 实现 LangGraph 状态机编排
  - [x] 编写 src/workflow.py: 定义所有节点（Init, Plan_Outline, Write_Method, Write_RelatedWork, Review_Citations, Render_Output）
  - [x] 编写 src/workflow.py: 实现条件边（Review 失败则打回对应 Write 节点）
  - [x] 编写 src/workflow.py: 编译状态图并导出 graph 对象

- [x] **Task 5**: 实现模板渲染和系统入口
  - [x] 编写 src/render.py: 使用 Jinja2 读取模板文件，注入 drafts 内容
  - [x] 完善 main.py: 整合所有模块，提供 run(topic, template_path) 接口
  - [x] 添加使用说明文档（README 或注释）

- [x] **Task 6**: 测试与验证
  - [x] 创建测试用例：模拟 .bib 文件解析
  - [x] 创建测试用例：验证引文幻觉检测
  - [x] 创建测试用例：验证模板渲染
  - [x] 运行端到端测试（核心逻辑测试通过 3/4）

## Task Dependencies
- Task 2 依赖于 Task 1（目录结构）
- Task 3 依赖于 Task 2（RAG 检索器）
- Task 4 依赖于 Task 3（Agent 节点）
- Task 5 依赖于 Task 4（工作流）
- Task 6 依赖于 Task 5（完整系统）

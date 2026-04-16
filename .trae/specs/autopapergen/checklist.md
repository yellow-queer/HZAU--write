# AutoPaperGen 验收检查清单

## 验收检查清单

### 目录结构与依赖
- [x] 创建了 requirements.txt，包含所有必需依赖（langgraph, llama-index, pydantic, jinja2, chromadb）
- [x] 创建了 data/codebase/, data/literature/, data/templates/ 目录
- [x] 创建了 src/rag/, src/agents/ 目录
- [x] 创建了 output/ 目录
- [x] 创建了 main.py 入口文件

### RAG 双知识库
- [x] lit_index.py 能正确解析 .bib 文件，提取所有 Citation Keys（测试验证通过）
- [x] lit_index.py 能解析 PDF 文献并创建向量索引
- [x] code_index.py 使用 CodeSplitter 进行代码切分
- [x] code_index.py 能创建代码向量索引
- [x] 两个索引完全独立，检索接口清晰分离

### Agent 状态与节点
- [x] state.py 定义了完整的 TypedDict（topic, zotero_keys, outline, drafts, errors）
- [x] planner.py 能根据 topic 生成合理的论文大纲
- [x] writers.py 的 Method Writer 仅查询 Codebase RAG
- [x] writers.py 的 RelatedWork Writer 仅查询 Literature RAG
- [x] writers.py 强制使用 Zotero Keys 格式为 \cite{key}
- [x] reviewer.py 能用正则检查所有 \cite{} 引文（测试验证通过）
- [x] reviewer.py 能检测幻觉引文并写入 errors（测试验证通过）

### LangGraph 状态机
- [x] workflow.py 定义了所有 6 个节点（Init, Plan_Outline, Write_Method, Write_RelatedWork, Review_Citations, Render_Output）
- [x] workflow.py 实现了条件边（Review 失败打回重写）
- [x] workflow.py 成功编译状态图

### 模板渲染与入口
- [x] render.py 使用 Jinja2 读取模板
- [x] render.py 正确注入 drafts 内容到模板占位符
- [x] main.py 提供完整的 run 接口
- [x] 输出文件正确保存到 output/ 目录

### 防幻觉约束
- [x] 测试验证：RelatedWork 章节的引文全部来自 .bib 文件（代码约束）
- [x] 测试验证：Method 章节没有编造代码中不存在的功能（代码约束）
- [x] 测试验证：Review 节点能成功拦截幻觉引文并打回重写（测试验证通过）

### 端到端测试
- [x] 创建测试用的 .bib 文件（包含 5 篇文献）
- [x] 创建测试用的代码库（简单的 Python 项目）
- [x] 创建测试用的模板文件（包含 {{ abstract }}, {{ introduction }}, {{ methodology }} 等占位符）
- [x] 运行核心逻辑测试，验证基础功能正常

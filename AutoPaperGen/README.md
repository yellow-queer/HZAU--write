# AutoPaperGen - 学术论文初稿自动生成系统

基于多 Agent 协作和 RAG 技术的学术论文初稿自动生成系统。基于给定的研究主题、用户科研工作内容、项目代码库和参考文献库，自动生成符合指定模板格式的论文初稿。

## 核心特性

- **EndNote 文献管理**：支持解析 EndNote 导出的 .ris 和 .txt 文件
- **姓名+年份引文格式**：遵循华中农业大学论文规范，如"（梅明华 1994）"、"(Smith et al 1993)"
- **用户科研内容输入**：通过 YAML 文件输入科研工作内容，指导论文写作
- **三层架构**：数据与索引层 / Agent 编排层 / 验证与对齐层
- **Qwen API 集成**：使用通义千问大模型作为 LLM 后端
- **防幻觉机制**：引文验证和事实核查
- **6章独立撰写**：每个章节由独立 Agent 撰写，使用对应知识库

## 目录结构

```
AutoPaperGen/
├── data/
│   ├── codebase/                    # 项目源代码
│   ├── literature/                  # 文献 PDF + EndNote 导出文件(.ris/.txt)
│   ├── templates/                   # 论文模板
│   ├── research_context.yaml        # 用户科研工作内容
│   └── research_context_template.yaml  # 科研内容输入模板
├── src/
│   ├── rag/                         # 数据与索引层
│   │   ├── code_index.py            # 代码库 RAG (CodeSplitter)
│   │   ├── lit_index.py             # 文献库 RAG (RIS/TXT/PDF)
│   │   └── style_index.py           # 风格库 RAG
│   ├── agents/                      # Agent 编排层
│   │   ├── state.py                 # 状态定义
│   │   ├── planner.py               # 大纲生成
│   │   ├── writers.py               # 6章独立撰写
│   │   ├── reviewer.py              # 引文校验
│   │   ├── fact_checker.py          # 事实核查
│   │   ├── literature_reviewer.py   # 文献研究员
│   │   └── code_analyst.py          # 代码分析员
│   ├── utils/
│   │   └── qwen_config.py           # Qwen API 配置
│   ├── workflow_hzau.py             # LangGraph 工作流
│   └── render.py                    # Jinja2 模板渲染
├── tests/
│   └── test_core.py                 # 核心逻辑测试
├── main.py                          # 系统入口
├── requirements.txt                 # 依赖列表
└── .env                             # Qwen API Key 配置
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

在 `.env` 文件中配置：

```
QWEN_API_KEY=your_api_key_here
QWEN_MODEL=qwen-plus
```

### 3. 准备数据

- 将项目源代码放入 `data/codebase/`
- 从 EndNote 导出文献信息到 `data/literature/`（支持 .ris 和 .txt 格式）
- 将文献 PDF 放入 `data/literature/`
- 编辑 `data/research_context.yaml` 填写科研工作内容

### 4. 运行系统

```bash
# 基本用法
python main.py "基于序列图像融合的实蝇侵染柑橘无损检测方法研究"

# 指定模板和科研内容
python main.py "研究主题" data/templates/hzau_thesis.md --context data/research_context.yaml
```

## 引文格式说明

系统使用"姓名+年份"引文格式，遵循华中农业大学论文规范：

| 作者数量  | 中文格式           | 英文格式                   |
| ----- | -------------- | ---------------------- |
| 1名    | （梅明华 1994）     | (Smith 1990)           |
| 2名    | （梅明华和李泽炳 1995） | (Smith and Jones 1992) |
| 3名及以上 | （梅明华等 1996）    | (Smith et al 1993)     |

同一括弧多篇文献按年代排序，逗号分隔：`(Smith 1990, Vaswani 2017)`

## 科研内容输入

通过 `data/research_context.yaml` 文件输入科研工作内容，系统会在写作时优先参考这些内容：

- `title`: 论文标题
- `research_summary`: 研究概述
- `innovations`: 核心创新点
- `methodology`: 方法论（数据采集、模型架构、对比模型、训练策略）
- `experiment_results`: 实验结果（环境、指标、发现）
- `system_implementation`: 系统实现（架构、功能）
- `limitations_and_future`: 不足与展望
- `additional_notes`: 补充说明

## 工作流

1. **Init** → 初始化 RAG 检索器，解析文献文件
2. **Plan\_Outline** → 根据研究主题和科研内容生成大纲
3. **Write Chapter 1-6** → 各章节独立撰写（绪论用文献库，2-5章用代码库，第6章综合）
4. **Fact\_Check** → 事实核查（代码一致性）
5. **Review\_Citations** → 引文校验（检测幻觉引文）
6. **Render** → Jinja2 模板渲染输出

## 技术栈

- **LangGraph** - 多 Agent 状态机编排
- **LlamaIndex** - RAG 与检索
- **Qwen API** - 大语言模型
- **ChromaDB** - 向量数据库
- **Jinja2** - 模板渲染
- **Pydantic** - 数据验证

##

主程序运行的逻辑是什么样的，是否能具有字数限制等其他论文写作时候要涉及的因素的交互修改内容，

# AutoPaperGen - 学术论文初稿自动生成系统
！！需要根据所写主题，在AutoPaperGen\src\agents\writers.py代码中进行prompt修改
！！AutoPaperGen/src/agents/planner.py中DEFAULT_OUTLINE为yaml文件解析错误的默认结果，担心错误可以进行修改
！！

基于多 Agent 协作和 RAG 技术的学术论文初稿自动生成系统。基于给定的研究主题、用户科研工作内容、参考文献库，自动生成符合指定模板格式的论文初稿。
> **说明**：代码库为**可选功能**。系统支持两种使用模式：
> - **完整模式**：提供代码库 + 文献库，生成更详细的技术章节
> - **文献模式**：仅提供文献库，适合纯理论研究或无代码项目

## 核心特性

- **EndNote 文献管理**：支持解析 EndNote 导出的 .xml、.ris 和 .txt 文件
- **姓名 + 年份引文格式**：遵循华中农业大学论文规范，如"（梅明华 1994）"、"(Smith et al 1993)"
- **用户科研内容输入**：通过 YAML 文件输入科研工作内容，指导论文写作
- **写作指令支持**：支持字数限制、写作重心、特殊要求等参数
- **三层架构**：数据与索引层 / Agent 编排层 / 验证与对齐层
- **Qwen API 集成**：使用通义千问大模型作为 LLM 后端
- **防幻觉机制**：引文验证和事实核查
- **6 章独立撰写**：每个章节由独立 Agent 撰写，使用对应知识库
- **代码库可选**：支持仅使用文献库运行，灵活适应不同研究场景

## 用户操作指南

### 完整使用流程

```
1. 安装依赖 → 2. 配置 API → 3. 准备数据 → 4. 编辑科研内容 → 5. 运行系统 → 6. 查看结果
```

### 步骤 1：安装依赖

```bash
pip install -r requirements.txt
```

### 步骤 2：配置 Qwen API Key

编辑项目根目录的 `.env` 文件：

```env
QWEN_API_KEY=your_api_key_here
QWEN_MODEL=qwen-plus
```

> **注意**：需要申请阿里云 Qwen API 服务获取 API Key

### 步骤 3：准备数据

系统支持两种使用模式，根据你的实际情况选择：

---

#### 场景一：完整模式（代码库 + 文献库）

适合有完整项目代码的研究，可生成更详细的技术章节。

**3.1 准备代码库**
将你的项目源代码放入 `data/codebase/` 目录：
```
data/codebase/
├── models/           # 模型代码
├── utils/            # 工具函数
├── train.py          # 训练脚本
└── ...
```

**3.2 准备文献库**
按照下方"文献资料准备"步骤操作。

**优点**：
- 第 2-5 章（方法、实验、系统）内容更具体
- 代码事实核查更准确
- 技术细节描述更丰富

---

#### 场景二：文献模式（仅文献库）

适合纯理论研究、综述论文，或暂无代码的项目。

**只需准备文献库**，按照下方"文献资料准备"步骤操作。

**优点**：
- 准备工作更简单
- 启动速度更快
- 适合早期研究阶段

---

#### 文献资料准备（两种模式都必须）

**方式 A：使用 EndNote 导出的 XML 文件（推荐）**
1. 在 EndNote 中选择要导出的文献
2. 导出为 XML 格式，文件名为 `柑橘.xml`（或其他名称）
3. 将 XML 文件放入 `data/literature/` 目录
4. 将对应的 PDF 文件放入 `data/literature/pdf/` 目录

**方式 B：使用 EndNote 导出的 RIS/TXT 文件**
1. 在 EndNote 中导出文献为 `.ris` 或 `.txt` 格式
2. 将导出文件放入 `data/literature/` 目录
3. 将文献 PDF 放入 `data/literature/` 目录

#### 3.3 论文模板（可选）
系统默认使用 `data/templates/hzau_thesis.md`（华中农业大学模板）
如有自定义模板，可放在任意位置，运行时指定路径

### 步骤 4：编辑科研工作内容（重要）

编辑 `data/research_context.yaml` 文件，填写你的研究内容：

```yaml
# research_context.yaml
title: "基于序列图像融合的实蝇侵染柑橘无损检测方法研究"

research_summary: |
  简要描述你的研究背景、目标和主要工作内容

innovations:
  - 创新点 1：例如"提出了多视角注意力融合机制"
  - 创新点 2：例如"构建了柑橘实蝇检测数据集"
  - 创新点 3：例如"开发了智能检测与问答系统"

methodology:
  data_collection: |
    数据采集方法，例如"使用多视角相机采集柑橘图像"
  model_architecture: |
    模型架构描述，例如"基于 YOLOv8 改进的检测模型"
  comparison_models: |
    对比的基线模型，例如"Faster R-CNN, SSD, YOLOv5"
  training_strategy: |
    训练策略，例如"使用迁移学习，学习率 0.001"

experiment_results:
  environment: |
    实验环境，例如"PyTorch 1.10, NVIDIA RTX 3090"
  metrics: |
    评估指标，例如"mAP, Precision, Recall, F1-Score"
  findings: |
    主要发现，例如"所提方法 mAP 达到 92.3%，优于基线模型"

system_implementation:
  architecture: |
    系统架构，例如"前后端分离架构，Flask 后端，Vue 前端"
  functions: |
    功能模块，例如"图像上传、实时检测、结果可视化、在线问答"

limitations_and_future: |
  当前工作的不足和未来改进方向

additional_notes:
  - 其他需要说明的内容
```

> **提示**：可以使用 `data/research_context_template.yaml` 作为参考模板

### 步骤 5：运行系统

#### 方式 A：交互式输入（推荐，适合新手）

直接运行命令，系统会逐步引导你输入必要参数：

```bash
python main.py
```

**交互式输入流程示例：**

```
============================================================
AutoPaperGen - 学术论文初稿自动生成系统
============================================================

欢迎使用交互式输入模式，我将引导您完成论文生成配置

请输入研究主题（必需）：基于序列图像融合的实蝇侵染柑橘无损检测方法研究
是否加载代码库？(y/n) [y]: y  # 输入 n 可跳过代码库加载，仅使用文献库
科研工作内容文件路径 [data/research_context.yaml]：  # 直接回车使用默认值
论文模板文件路径 [data/templates/hzau_thesis.md]：  # 直接回车使用默认值
每章节最少字数 [2000]：3000  # 可自定义或回车使用默认值
写作重心描述（可选，直接回车跳过）：重点分析实验结果和模型性能

特殊写作要求（可选，每行一条，输入空行结束）：
  要求 1: 避免复杂公式
  要求 2: 强调应用价值
  要求 3:   # 输入空行表示结束

============================================================
配置摘要
============================================================
研究主题：基于序列图像融合的实蝇侵染柑橘无损检测方法研究
代码库：已启用
科研内容：data/research_context.yaml
论文模板：data/templates/hzau_thesis.md
字数限制：3000 字
写作重心：重点分析实验结果和模型性能
特殊要求：
  1. 避免复杂公式
  2. 强调应用价值
============================================================

确认开始生成论文？(y/n) [y]:   # 输入 y 确认开始
```

> **提示**：如果选择不加载代码库（输入 `n`），系统将仅使用文献库生成论文，适合纯理论研究或暂无代码的项目。

#### 方式 B：命令行参数（适合高级用户）

```bash
python main.py "研究主题" \
  --context data/research_context.yaml \
  --word-limit 3000 \
  --focus "重点分析实验结果和模型性能" \
  --notes "避免复杂公式" \
  --notes "强调应用价值"
```

#### 参数说明

| 参数 | 说明 | 默认值 | 示例 |
|-----|------|--------|------|
| `topic` | 研究主题（必需） | - | `"基于序列图像融合的实蝇侵染柑橘无损检测方法研究"` |
| `template_path` | 论文模板路径（可选） | 默认模板 | `data/templates/hzau_thesis.md` |
| `--context` | 科研工作内容文件路径 | `data/research_context.yaml` | `data/research_context.yaml` |
| `--word-limit` | 每章节最少字数 | 2000 | `3000` |
| `--focus` | 写作重心描述 | 无 | `"重点分析实验结果"` |
| `--notes` | 特殊要求（可多次） | 无 | `--notes "避免公式" --notes "强调应用"` |

#### 更多示例

```bash
# 使用自定义模板
python main.py "研究主题" data/templates/custom.md

# 指定科研内容文件
python main.py "研究主题" --context my_research.yaml

# 设置字数限制和写作重心
python main.py "研究主题" --word-limit 4000 --focus "模型创新点"

# 添加多个特殊要求
python main.py "研究主题" --notes "使用图表说明" --notes "避免专业术语"
```

### 步骤 6：查看结果

运行完成后，系统会在 `output/` 目录生成最终论文：

```
output/
└── paper.md    # 生成的论文初稿
```

使用 Markdown 阅读器或文本编辑器打开查看。

## 引文格式说明

系统使用"姓名 + 年份"引文格式，遵循华中农业大学论文规范：

| 作者数量 | 中文格式 | 英文格式 |
| ----- | -------------- | ---------------------- |
| 1 名 | （梅明华 1994） | (Smith 1990) |
| 2 名 | （梅明华和李泽炳 1995） | (Smith and Jones 1992) |
| 3 名及以上 | （梅明华等 1996） | (Smith et al 1993) |

同一括弧多篇文献按年代排序，逗号分隔：`(Smith 1990, Vaswani 2017)`

## 工作流

1. **Init** → 初始化 RAG 检索器，解析文献文件
2. **Plan_Outline** → 根据研究主题和科研内容生成 6 章大纲
3. **Write Chapter 1-6** → 各章节独立撰写
   - 第 1 章（绪论）：使用文献库
   - 第 2-5 章（方法、实验、系统）：使用代码库
   - 第 6 章（总结）：综合所有内容
4. **Fact_Check** → 事实核查（代码一致性）
5. **Review_Citations** → 引文校验（检测幻觉引文）
6. **Render** → Jinja2 模板渲染输出

## 技术栈

- **LangGraph** - 多 Agent 状态机编排
- **LlamaIndex** - RAG 与检索
- **Qwen API** - 大语言模型
- **ChromaDB** - 向量数据库
- **Jinja2** - 模板渲染
- **Pydantic** - 数据验证
- **EndNote XML/RIS** - 文献管理

## 适配其他课题

本系统支持任意学科和研究主题的论文写作。以下是适配其他课题的关键步骤：

### 1. 自定义章节名称

在 `data/research_context.yaml` 中添加 `chapters` 配置：

```yaml
chapters:
  write_chapter1: "1 绪论"
  write_chapter2: "2 研究方法与数据"      # 可改为你的章节名称
  write_chapter3: "3 模型设计与实现"      # 如 "3 实验设计"
  write_chapter4: "4 实验结果与分析"
  write_chapter5: "5 系统开发与应用"      # 如 "5 案例研究"
  write_chapter6: "6 总结与展望"
```

### 2. 配置代码检索章节

如果你的研究涉及代码，可指定哪些章节需要代码检索：

```yaml
code_chapter_keys:
  - write_chapter2    # 这些章节会使用代码库内容
  - write_chapter3
  - write_chapter4
  - write_chapter5
```

### 3. 不同学科示例

| 学科类型 | 推荐章节结构 | 是否需要代码库 |
|---------|-------------|--------------|
| **理工科（实验类）** | 绪论、方法、实验、结果、讨论、总结 | 推荐 |
| **理工科（系统类）** | 绪论、需求分析、设计、实现、测试、总结 | 必须 |
| **文科（理论类）** | 绪论、文献综述、理论框架、分析、结论 | 不需要 |
| **文科（实证类）** | 绪论、文献综述、方法、结果、讨论、结论 | 可选 |
| **综述类** | 绪论、主题A、主题B、主题C、展望、总结 | 不需要 |

### 4. 自定义论文模板

修改 `data/templates/hzau_thesis.md` 或创建新模板：

```markdown
# {{ title }}

## 1 {{ chapter_1_title | default('绪论') }}
{{ chapter_1 }}

## 2 {{ chapter_2_title | default('研究方法') }}
{{ chapter_2 }}
```

### 5. 完整示例参考

查看 `data/research_context_example.yaml` 了解完整填写示例。

## 常见问题

### Q: 我没有代码库，可以使用系统吗？
A: **完全可以！** 代码库是可选功能。你可以选择"文献模式"，仅使用文献库生成论文。系统会根据你的科研工作内容（research_context.yaml）和文献资料生成论文初稿，适合纯理论研究、综述论文或早期研究阶段。

### Q: 代码库加载需要多长时间？
A: 代码库加载时间取决于代码量大小：
- 小型项目（< 100 文件）：约 10-30 秒
- 中型项目（100-500 文件）：约 1-3 分钟
- 大型项目（> 500 文件）：可能需要 5 分钟以上

如果选择不加载代码库，系统启动会更快。

### Q: 不加载代码库会影响论文质量吗？
A: 影响有限，主要区别在于：
- **加载代码库**：第 2-5 章（方法、实验、系统）会有更具体的技术细节和代码引用
- **不加载代码库**：这些章节会更侧重于理论描述和方法论，依赖你提供的科研工作内容

建议：如果项目有代码，推荐加载；如果是纯理论研究，不加载完全没问题。

### Q: 必须提供项目代码吗？
A: 不是必须的。代码库是可选功能，你可以根据实际情况选择是否加载。

### Q: 文献必须提供 PDF 吗？
A: 系统主要使用 EndNote 导出的元数据（XML/RIS/TXT），PDF 用于辅助理解，建议提供。

### Q: 科研工作内容必须填写吗？
A: 强烈建议填写。不填写的话系统会根据主题自动生成，但可能不够准确反映你的实际工作。

### Q: 生成的论文可以直接使用吗？
A: 生成的是初稿，建议人工审阅、修改和完善后再使用。

### Q: 如何修改生成的论文？
A: 可以直接编辑 `output/paper.md` 文件，或者调整输入参数重新运行。

## 目录结构

```
AutoPaperGen/
├── data/
│   ├── codebase/                       # 项目源代码（可选）
│   ├── literature/                     # 文献 PDF + EndNote 导出文件
│   │   └── pdf/                        # 文献 PDF 文件
│   ├── templates/                      # 论文模板
│   │   └── hzau_thesis.md              # 默认模板（可自定义）
│   ├── research_context.yaml           # 用户科研工作内容（需填写）
│   └── research_context_example.yaml   # 完整示例（供参考）
├── src/
│   ├── rag/                            # 数据与索引层
│   │   ├── code_index.py               # 代码库 RAG
│   │   ├── lit_index.py                # 文献库 RAG
│   │   └── style_index.py              # 风格库 RAG
│   ├── agents/                         # Agent 编排层
│   │   ├── state.py                    # 状态定义
│   │   ├── planner.py                  # 大纲生成
│   │   ├── writers.py                  # 6 章独立撰写
│   │   ├── reviewer.py                 # 引文校验
│   │   ├── fact_checker.py             # 事实核查
│   │   └── output_writer.py            # 增量输出
│   ├── utils/
│   │   ├── qwen_config.py              # Qwen API 配置
│   │   └── interactive_input.py        # 交互式输入
│   ├── workflow_hzau.py                # LangGraph 工作流
│   └── render.py                       # Jinja2 模板渲染
├── tests/
│   └── test_core.py                    # 核心逻辑测试
├── main.py                             # 系统入口
├── requirements.txt                    # 依赖列表
├── .env.example                        # 环境变量示例
└── output/                             # 生成的论文输出
```

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

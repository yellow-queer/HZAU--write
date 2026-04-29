# AutoPaperGen - 学术论文初稿自动生成系统
这是基于华中农业大学HZAU论文格式要求的参考初稿生成系统
基于多 Agent 协作和 RAG 技术的学术论文初稿生成系统。**5 分钟快速上手**，支持灵活配置。

---

## 快速开始（5 步完成论文生成）

### 1️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

### 2️⃣ 配置 Qwen API

**（1）申请 API Key**
1. 访问 https://dashscope.console.aliyun.com/
2. 注册/登录阿里云账号
3. 开通 DashScope 服务
4. 创建 API Key（控制台 → API Key 管理）

**（2）配置文件**
编辑项目根目录的 `.env` 文件：
```env
QWEN_API_KEY=sk-你的 APIKey
QWEN_MODEL=qwen-plus
```

### 3️⃣ 准备数据

在 `data/` 目录下准备以下文件（**代码库和内容库可选**）：

```
data/
├── literature/              # 【必需】文献库
│   ├── 柑橘.xml            # EndNote 导出的文献
│   └── pdf/                # 文献 PDF（可选）
│       ├── 论文 1.pdf
│       └── 论文 2.pdf
│
├── codebase/               # 【可选】项目代码
│   ├── models/
│   └── train.py
│
├── content/                # 【可选】项目资料
│   ├── 实验结果.txt
│   └── 数据表格.xlsx
│
└── research_context.yaml   # 【必需】科研内容（见步骤 4）
```

**文献准备方法**：
- EndNote 中导出文献为 XML 格式 → 放入 `data/literature/`
- 文献 PDF → 放入 `data/literature/pdf/`

### 4️⃣ 填写科研内容

编辑 `data/research_context.yaml`：

```yaml
title: "你的论文题目"

research_summary: |
  研究背景和目标（200-300 字）

innovations:
  - 创新点 1
  - 创新点 2
  - 创新点 3

methodology:
  data_collection: 数据采集方法
  model_architecture: 模型架构
  comparison_models: 对比模型
  training_strategy: 训练策略

experiment_results:
  environment: 实验环境
  metrics: 评估指标
  findings: 主要发现

system_implementation:
  architecture: 系统架构
  functions: 功能模块

limitations_and_future: 不足与未来方向
```

> 💡 提示：参考 `data/research_context_example.yaml` 完整示例

### 5️⃣ 运行系统

```bash
python main.py
```

按提示输入：
- 研究主题
- 是否加载代码库（y/n）
- 是否加载内容库（y/n）
- 字数要求等

生成结果在 `output/paper.md`

---

## 适配新课题（4 处修改）

### 修改 1：章节名称（可选）

**文件**：`data/research_context.yaml`

```yaml
chapters:
  write_chapter1: "1 绪论"
  write_chapter2: "2 材料与方法"     # 改为你的章节名
  write_chapter3: "3 结果与分析"
  write_chapter4: "4 讨论"
  write_chapter5: "5 结论"
  write_chapter6: "6 展望"
```

### 修改 2：代码检索章节（如有代码）

**文件**：`data/research_context.yaml`

```yaml
code_chapter_keys:
  - write_chapter2    # 哪些章节需要引用代码
  - write_chapter3
```

### 修改 3：内容检索章节（如有项目资料）

**文件**：`data/research_context.yaml`

```yaml
content_chapter_keys:
  - write_chapter2    # 哪些章节需要引用内容库
  - write_chapter4
```
**注意！**：workflow_hzau.py 中设置有默认DEFAULT_CONTENT_CHAPTER_KEYS与DEFAULT_CODE_CHAPTER_KEYS，根据需要调整。
### 修改 4：论文模板（可选）

**文件**：`data/templates/hzau_thesis.md`

```markdown
# {{ title }}

## 1 {{ chapter_1_title | default('绪论') }}
{{ chapter_1 }}

## 2 {{ chapter_2_title | default('材料与方法') }}
{{ chapter_2 }}
```

---

## 命令行高级用法

```bash
# 基础用法
python main.py "研究主题"

# 指定参数
python main.py "研究主题" \
  --context data/research_context.yaml \
  --word-limit 3000 \
  --focus "重点分析实验结果" \
  --notes "避免公式" \
  --notes "强调应用"

# 自定义模板
python main.py "研究主题" data/templates/custom.md
```

---

## 常见问题

**Q: 没有代码能用吗？**  
A: 可以！代码库是可选的，纯理论研究只需文献库。

**Q: 支持哪些文件格式？**  
A: 
- 文献：EndNote XML/RIS/TXT
- 内容库：txt, md, pdf, docx, xlsx, jpg, png

**Q: 生成需要多久？**  
A: 通常 5-15 分钟，取决于代码量和文献数量。

**Q: 引文格式是什么？**  
A: 姓名 + 年份格式，如（梅明华 1994）或 (Smith et al 1993)

---

## 目录结构

```
AutoPaperGen/
├── data/
│   ├── codebase/           # 项目代码（可选）
│   ├── content/            # 项目资料（可选）
│   ├── literature/         # 文献库（必需）
│   ├── templates/          # 论文模板
│   └── research_context.yaml  # 科研内容（必需）
├── src/                    # 源代码
├── output/                 # 生成结果
├── main.py                 # 入口文件
└── requirements.txt        # 依赖
```

---

## 技术栈

LangGraph | LlamaIndex | Qwen API | ChromaDB | Jinja2

---

**提示**：生成的是初稿，建议人工审阅修改后使用。

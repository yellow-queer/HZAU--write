# AutoPaperGen 配置更新任务清单

## Tasks

- [x] **Task 1**: 集成 Qwen API
  - [x] 安装 qwen-sdk 或使用 openai 兼容接口
  - [x] 修改 main.py 以从 .env 读取 QWEN_API_KEY
  - [x] 配置 LLM 使用 Qwen API

- [x] **Task 2**: 更新论文模板格式
  - [x] 创建符合华中农业大学毕业论文模板的新模板
  - [x] 修改 template.md 包含 6 章结构
  - [x] 添加 LaTeX 模板支持（如需要）

- [x] **Task 3**: 更新 Agent Prompts
  - [x] 修改 planner.py 的 OUTLINE_PROMPT 以生成 6 章结构
  - [x] 修改 writers.py 的 prompts 以适配新章节名称
  - [x] 确保 Prompt 中包含用户提供的具体论文大纲内容

## Task Dependencies
- Task 2 依赖于 Task 1（模板需要配合 LLM）
- Task 3 依赖于 Task 2（Prompts 需要配合新模板）

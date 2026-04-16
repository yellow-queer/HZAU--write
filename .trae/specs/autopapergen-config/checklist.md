# AutoPaperGen 配置更新检查清单

## 验收检查清单

### Task 1: Qwen API 集成
- [x] main.py 能够从 .env 读取 QWEN_API_KEY
- [x] Qwen LLM 正确初始化
- [x] 能够成功调用 Qwen API 生成内容

### Task 2: 论文模板格式
- [x] 新模板包含 6 章结构（绪论、数据采集、模型构建、实验分析、系统实现、总结展望）
- [x] 模板支持中文输出
- [x] 格式符合华中农业大学毕业论文要求

### Task 3: Agent Prompts 更新
- [x] planner.py 生成的大纲包含用户提供的具体章节
- [x] writers.py 的 prompts 包含用户论文的具体内容指引
- [x] 所有章节名称使用中文

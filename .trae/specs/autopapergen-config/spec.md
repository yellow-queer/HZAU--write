# AutoPaperGen 配置更新 Spec

## Why
需要将 AutoPaperGen 系统配置为使用 Qwen API 作为 LLM，并根据华中农业大学本科毕业论文模板调整论文格式设置。

## What Changes
- **新增** Qwen API 集成配置
- **修改** 论文模板格式以符合华中农业大学毕业论文要求
- **修改** Agent Prompt 以适配新的论文章节结构

## Impact
- **受影响文件**: main.py, src/agents/planner.py, src/agents/writers.py, data/templates/
- **技术栈**: 新增 qwen-sdk 或兼容 OpenAI API 格式的调用

## ADDED Requirements

### Requirement: Qwen API 集成
系统 SHALL 支持使用 Qwen API 作为 LLM 后端，通过读取 .env 文件中的 QWEN_API_KEY 进行配置。

#### Scenario: 配置 Qwen API
- **WHEN** 系统启动时
- **THEN** 从 .env 文件读取 QWEN_API_KEY
- **AND** 初始化 Qwen LLM 实例

### Requirement: 华中农业大学论文格式
系统 SHALL 根据华中农业大学本科毕业论文模板调整输出格式，包括：
- 章节编号（1, 1.1, 1.1.1 等）
- 摘要、Abstract、关键词
- 参考文献格式
- 致谢

#### Scenario: 生成论文章节
- **WHEN** Planner Agent 生成大纲时
- **THEN** 按照用户提供的 6 章结构生成（绪论、数据采集、模型构建、实验分析、系统实现、总结展望）

## MODIFIED Requirements

### Requirement: 论文模板结构
原模板使用标准学术论文结构（Introduction, Methodology, Experiments, Related Work, Conclusion），现修改为符合用户论文的具体章节：

1. 绪论（含研究背景、国内外现状、研究内容）
2. 柑橘多视角图像采集与数据处理
3. 基于多视角注意力融合的检测模型构建
4. 实验结果与对比分析
5. 柑橘实蝇智能检测与问答系统设计与实现
6. 总结与展望

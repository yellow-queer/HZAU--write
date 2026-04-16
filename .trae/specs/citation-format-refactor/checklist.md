# 引文格式改造与项目清理验收检查清单

## 引文格式化引擎
- [x] format_citation 正确处理中文1名作者
- [x] format_citation 正确处理中文2名作者
- [x] format_citation 正确处理中文3+名作者
- [x] format_citation 正确处理英文1名作者
- [x] format_citation 正确处理英文2名作者
- [x] format_citation 正确处理英文3+名作者
- [x] generate_citation_texts 为所有文献生成格式化引文映射

## EndNote .txt 文件解析
- [x] parse_endnote_txt 能解析 EndNote 导出的标签式 .txt 文件
- [x] parse_literature_files 自动检测 .ris 和 .txt 文件
- [x] .txt 和 .ris 解析结果格式一致

## 引文校验
- [x] reviewer.py 不再使用 cite key 正则
- [x] 新校验逻辑能检测姓名+年份格式的引文
- [x] 幻觉引文检测正常工作
- [x] 校验失败时正确标记需重写的章节

## Writer Prompts
- [x] CHAPTER1 和 CHAPTER6 prompt 不再提及 cite key 格式
- [x] 所有 prompt 指示使用姓名+年份格式
- [x] prompt 中注入可用引文文本列表
- [x] CHAPTER1 的 citation_keys 占位符已替换为 citation_texts

## render.py 和 main.py
- [x] main.py 调用 generate_citation_texts 并放入 initial_state
- [x] state.py 包含 citation_texts 字段
- [x] render.py 渲染上下文包含参考文献列表

## 冗余文件清理
- [x] 使用说明.md 已删除
- [x] 华中农业大学配置说明.md 已删除
- [x] 项目总结.md 已删除
- [x] tests/test_autopapergen.py 已删除
- [x] README.md 已创建且内容准确

## README.md 内容准确性
- [x] 提及 EndNote 文献管理
- [x] 提及 .ris 和 .txt 文件格式
- [x] 提及姓名+年份引文格式
- [x] 提及三层架构
- [x] 提及 research_context 功能
- [x] 提及 Qwen API 配置
- [x] 目录结构反映当前实际文件

## 测试
- [x] 所有测试通过（15/15）
- [x] 引文格式化测试覆盖1/2/3+作者的中英文场景
- [x] EndNote .txt 解析测试通过
- [x] 新引文校验测试通过
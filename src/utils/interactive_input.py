"""
交互式输入模块

提供友好的命令行交互式输入界面，引导用户逐步输入必要参数
"""

from pathlib import Path
from typing import Optional, List


def print_welcome():
    """打印欢迎信息"""
    print("\n" + "=" * 60)
    print("AutoPaperGen - 学术论文初稿自动生成系统")
    print("=" * 60)
    print("\n欢迎使用交互式输入模式，我将引导您完成论文生成配置\n")


def get_topic() -> str:
    """获取研究主题（必需）"""
    while True:
        topic = input("请输入研究主题（必需）：").strip()
        if topic:
            return topic
        print("❌ 研究主题不能为空，请重新输入\n")


def get_context_file(default: str = "data/research_context.yaml") -> Optional[str]:
    """获取科研工作内容文件路径（可选）"""
    while True:
        path = input(f"科研工作内容文件路径 [{default}]：").strip()
        
        if not path:
            # 用户直接回车，使用默认值
            if Path(default).exists():
                print(f"✓ 使用默认文件：{default}")
                return default
            else:
                print(f"⚠ 默认文件不存在，将跳过科研内容输入")
                return None
        
        # 验证文件是否存在
        if Path(path).exists():
            print(f"✓ 已加载科研内容文件：{path}")
            return path
        else:
            print(f"⚠ 文件不存在：{path}")
            retry = input("是否继续？(y/n) [y]: ").strip().lower()
            if retry != 'n':
                return path


def get_template_file(default: str = "data/templates/hzau_thesis.md") -> Optional[str]:
    """获取论文模板文件路径（可选）"""
    while True:
        path = input(f"论文模板文件路径 [{default}]：").strip()
        
        if not path:
            # 用户直接回车，使用默认值
            if Path(default).exists():
                print(f"✓ 使用默认模板：{default}")
                return default
            else:
                print(f"⚠ 默认模板不存在，将创建基础模板")
                return None
        
        # 验证文件是否存在
        if Path(path).exists():
            print(f"✓ 已加载模板文件：{path}")
            return path
        else:
            print(f"⚠ 模板文件不存在：{path}")
            retry = input("是否继续？(y/n) [y]: ").strip().lower()
            if retry != 'n':
                return path


def get_word_limit(default: int = 2000) -> int:
    """获取每章节字数限制（可选）"""
    while True:
        value = input(f"每章节最少字数 [{default}]：").strip()
        
        if not value:
            print(f"✓ 使用默认值：{default} 字")
            return default
        
        try:
            word_limit = int(value)
            if word_limit > 0:
                print(f"✓ 字数限制：{word_limit} 字")
                return word_limit
            else:
                print("❌ 字数必须大于 0，请重新输入\n")
        except ValueError:
            print("❌ 请输入有效的数字，或直接回车使用默认值\n")


def get_focus() -> str:
    """获取写作重心（可选）"""
    focus = input("写作重心描述（可选，直接回车跳过）：").strip()
    if focus:
        print(f"✓ 写作重心：{focus}")
    else:
        print("✓ 跳过写作重心设置")
    return focus


def get_notes() -> List[str]:
    """获取特殊要求（可选，支持多个）"""
    print("\n特殊写作要求（可选，每行一条，输入空行结束）：")
    notes = []
    
    while True:
        note = input(f"  要求 {len(notes) + 1}: ").strip()
        
        if not note:
            if notes:
                print(f"✓ 已添加 {len(notes)} 条特殊要求")
            else:
                print("✓ 跳过特殊要求设置")
            break
        
        notes.append(note)
    
    return notes


def get_load_codebase(default: bool = False) -> bool:
    """获取是否加载代码库的选项"""
    print("\n" + "-" * 40)
    print("代码库加载选项：")
    print("  - 选择 'y': 将加载代码库并构建索引（可能需要几分钟）")
    print("  - 选择 'n': 跳过代码库加载，仅使用文献库生成论文")
    print("-" * 40)
    
    default_str = "y" if default else "n"
    while True:
        value = input(f"是否加载代码库？(y/n) [{default_str}]: ").strip().lower()
        
        if not value:
            print(f"✓ 使用默认值：{'加载代码库' if default else '跳过代码库加载'}")
            return default
        
        if value in ('y', 'yes'):
            print("✓ 将加载代码库并构建索引")
            return True
        elif value in ('n', 'no'):
            print("✓ 跳过代码库加载")
            return False
        else:
            print("❌ 请输入 'y' 或 'n'，或直接回车使用默认值\n")


def print_summary(topic: str, context: Optional[str], template: Optional[str], 
                  word_limit: int, focus: str, notes: List[str], load_codebase: bool):
    """打印配置摘要"""
    print("\n" + "=" * 60)
    print("配置摘要")
    print("=" * 60)
    print(f"研究主题：{topic}")
    print(f"科研内容：{context if context else '（无）'}")
    print(f"论文模板：{template if template else '（使用默认模板）'}")
    print(f"字数限制：{word_limit} 字")
    print(f"写作重心：{focus if focus else '（无）'}")
    print(f"加载代码库：{'是' if load_codebase else '否'}")
    if notes:
        print("特殊要求：")
        for i, note in enumerate(notes, 1):
            print(f"  {i}. {note}")
    print("=" * 60)
    confirm = input("\n确认开始生成论文？(y/n) [y]: ").strip().lower()
    
    if confirm == 'n':
        print("\n❌ 已取消")
        return False
    
    print("\n✓ 开始生成论文...\n")
    return True


def get_interactive_inputs() -> dict:
    """
    获取所有交互式输入
    
    Returns:
        包含所有输入的字典：
        - topic: str
        - context_path: Optional[str]
        - template_path: Optional[str]
        - word_limit: int
        - focus: str
        - writing_notes: List[str]
        - load_codebase: bool
    """
    print_welcome()
    
    topic = get_topic()
    context_path = get_context_file()
    template_path = get_template_file()
    word_limit = get_word_limit()
    focus = get_focus()
    writing_notes = get_notes()
    load_codebase = get_load_codebase()
    
    # 打印配置摘要并确认
    if not print_summary(topic, context_path, template_path, word_limit, focus, writing_notes, load_codebase):
        exit(0)
    
    return {
        "topic": topic,
        "context_path": context_path,
        "template_path": template_path,
        "word_limit": word_limit,
        "focus": focus,
        "writing_notes": writing_notes,
        "load_codebase": load_codebase,
    }

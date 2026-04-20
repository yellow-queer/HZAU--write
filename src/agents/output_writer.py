import os
import re
from datetime import datetime
from typing import List


def init_output_file(output_file: str, title: str) -> bool:
    try:
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        content = f"# {title}\n\n生成时间：{current_time}\n\n---\n\n"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)

        return True
    except Exception as e:
        print(f"初始化输出文件失败: {e}")
        return False


def write_chapter_to_file(output_file: str, chapter_name: str, content: str) -> bool:
    try:
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        chapter_content = f"## {chapter_name}\n\n{content}\n\n---\n\n"

        with open(output_file, "a", encoding="utf-8") as f:
            f.write(chapter_content)

        return True
    except Exception as e:
        print(f"写入章节失败: {e}")
        return False


def get_completed_chapters(output_file: str) -> List[str]:
    if not os.path.exists(output_file):
        return []

    try:
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()

        pattern = r"^## (.+)$"
        chapters = re.findall(pattern, content, re.MULTILINE)

        return chapters
    except Exception as e:
        print(f"读取已完成章节失败: {e}")
        return []

# {{ title | default('论文标题') }}

## 摘要

{{ abstract }}

**关键词**：{{ keywords | default('关键词 1; 关键词 2; 关键词 3') }}

---

## Abstract

{{ english_abstract }}

**Keywords**: {{ english_keywords | default('keyword1; keyword2; keyword3') }}

---

## 目录

{% for chapter_key, chapter_name in chapters.items() %}
{{ chapter_key }} {{ chapter_name }}
{% endfor %}

---

{% for chapter_key, chapter_name in chapters.items() %}
## {{ chapter_key }} {{ chapter_name }}

{{ drafts.get(chapter_name, '') }}

---
{% endfor %}

## 参考文献

{{ references }}

---

## 致谢

{{ acknowledgments }}

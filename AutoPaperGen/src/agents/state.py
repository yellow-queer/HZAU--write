from typing import TypedDict, List, Dict, Any


class PaperDraftState(TypedDict):
    topic: str
    citation_keys: List[str]
    outline: Dict[str, str]
    drafts: Dict[str, str]
    errors: List[str]
    current_section: str
    max_retries: int
    retries: int
    sections_to_rewrite: List[str]
    llm: Any
    literature_retriever: Any
    code_retriever: Any
    style_retriever: Any
    research_context: Dict[str, Any]
    citation_texts: Dict[str, str]

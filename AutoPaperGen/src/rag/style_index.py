"""
风格知识库 RAG 索引模块

负责：
1. 解析论文模板和已有论文文本
2. 使用 SentenceSplitter 构建风格向量库
3. 提供风格检索接口，确保生成内容风格一致
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    Settings,
    Document
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb


class StyleIndex:
    """风格知识库索引"""

    def __init__(self, style_dir: str = "data/templates", persist_dir: str = ".chroma_style"):
        self.style_dir = Path(style_dir)
        self.persist_dir = persist_dir
        self.index: Optional[VectorStoreIndex] = None
        self.query_engine = None

    def build_index(self, llm=None, embed_model=None):
        """构建风格向量索引"""
        if embed_model:
            Settings.embed_model = embed_model
        if llm:
            Settings.llm = llm

        documents = []

        for ext in ['*.md', '*.tex', '*.txt']:
            for f in self.style_dir.glob(ext):
                with open(f, 'r', encoding='utf-8') as file:
                    content = file.read()
                doc = Document(
                    text=content,
                    metadata={'source': f.name, 'type': 'style_template'}
                )
                documents.append(doc)

        if not documents:
            print("警告：没有找到风格参考文件")
            return

        db = chromadb.PersistentClient(path=self.persist_dir)
        chroma_collection = db.get_or_create_collection("style")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=32)
        self.index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            node_parser=node_parser
        )

        self.query_engine = self.index.as_query_engine(similarity_top_k=3)
        print(f"风格索引构建完成，共 {len(documents)} 个文档")

    def query(self, query_str: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """查询风格索引"""
        if self.query_engine is None:
            raise RuntimeError("索引未初始化")
        response = self.query_engine.query(query_str)
        results = []
        if hasattr(response, 'source_nodes'):
            for node in response.source_nodes:
                results.append({
                    'text': node.node.text,
                    'metadata': node.node.metadata,
                    'score': node.score if hasattr(node, 'score') else None
                })
        return results

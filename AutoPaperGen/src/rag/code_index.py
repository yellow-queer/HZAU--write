"""
代码知识库 RAG 索引模块

负责：
1. 使用 CodeSplitter 切分代码库，保留 AST 结构
2. 为代码创建 LlamaIndex 向量索引
3. 提供代码检索接口
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
from llama_index.core.node_parser import CodeSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb


class CodebaseIndex:
    """代码知识库索引"""
    
    def __init__(self, codebase_dir: str, persist_dir: str = ".chroma_codebase"):
        """
        初始化代码索引
        
        Args:
            codebase_dir: 代码库目录路径
            persist_dir: ChromaDB 持久化目录
        """
        self.codebase_dir = Path(codebase_dir)
        self.persist_dir = persist_dir
        self.index: Optional[VectorStoreIndex] = None
        self.query_engine = None
        
    def build_index(self, llm=None, embed_model=None):
        """
        构建代码向量索引
        
        Args:
            llm: LLM 模型（可选）
            embed_model: 嵌入模型（可选）
        """
        if embed_model:
            Settings.embed_model = embed_model
        if llm:
            Settings.llm = llm
        
        documents = []
        
        # 支持的语言及其扩展名
        supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin'
        }
        
        # 遍历代码库目录
        for ext, language in supported_extensions.items():
            code_files = list(self.codebase_dir.rglob(f"*{ext}"))
            
            for code_file in code_files:
                try:
                    with open(code_file, 'r', encoding='utf-8') as f:
                        code_content = f.read()
                    
                    # 跳过空文件或过大的文件
                    if not code_content.strip() or len(code_content) > 100000:
                        continue
                    
                    doc = Document(
                        text=code_content,
                        metadata={
                            'source': str(code_file.relative_to(self.codebase_dir)),
                            'language': language,
                            'file_name': code_file.name
                        }
                    )
                    documents.append(doc)
                    
                except Exception as e:
                    print(f"读取代码文件失败 {code_file}: {e}")
        
        if not documents:
            print(f"警告：未在 {self.codebase_dir} 中找到支持的代码文件")
            return
        
        # 使用 CodeSplitter 进行 AST 感知的代码切分
        code_splitter = CodeSplitter(
            language="python",  # 默认使用 Python，实际使用时可以根据文件类型动态选择
            chunk_lines=40,
            chunk_lines_overlap=10,
            max_chars=1500
        )
        
        # 创建 ChromaDB 向量存储
        db = chromadb.PersistentClient(path=self.persist_dir)
        chroma_collection = db.get_or_create_collection("codebase")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # 创建索引
        self.index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            transformations=[code_splitter]
        )
        
        # 创建查询引擎
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=5,
            include_metadata=True
        )
        
        print(f"代码索引构建完成，共 {len(documents)} 个代码文件")
    
    def query(self, query_str: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        查询代码索引
        
        Args:
            query_str: 查询字符串
            top_k: 返回结果数量
            
        Returns:
            查询结果列表
        """
        if self.query_engine is None:
            raise RuntimeError("索引未初始化，请先调用 build_index()")
        
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
    
    def query_by_file(self, file_path: str, query_str: str) -> List[Dict[str, Any]]:
        """
        在指定文件中查询
        
        Args:
            file_path: 文件路径（相对于 codebase_dir）
            query_str: 查询字符串
            
        Returns:
            查询结果列表
        """
        if self.query_engine is None:
            raise RuntimeError("索引未初始化")
        
        # 可以通过过滤元数据实现文件级别的精确查询
        results = self.query(query_str)
        
        # 过滤出指定文件的结果
        filtered_results = [
            r for r in results 
            if r['metadata'].get('source') == file_path
        ]
        
        return filtered_results

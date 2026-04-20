"""
代码知识库 RAG 索引模块

负责：
1. 使用 CodeSplitter 切分代码库，保留 AST 结构
2. 为代码创建 LlamaIndex 向量索引
3. 提供代码检索接口
"""

import os
import sys
import time
import signal
import threading
from typing import List, Dict, Any, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from functools import wraps

from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    Settings,
    Document
)
from llama_index.core.node_parser import CodeSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb


TREE_SITTER_CACHE_DIRS = [
    Path.home() / ".cache" / "tree-sitter",
    Path.home() / ".tree-sitter",
    Path.home() / "AppData" / "Local" / "tree-sitter" if sys.platform == "win32" else None,
]

MANUAL_DOWNLOAD_GUIDE = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    Tree-sitter Parser 手动下载指引                            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  问题：tree-sitter parser 下载超时或失败                                      ║
║                                                                              ║
║  解决方案 1：使用 pip 安装预编译包                                            ║
║    pip install tree-sitter-language-pack                                     ║
║                                                                              ║
║  解决方案 2：手动下载 parser 文件                                             ║
║    1. 访问: https://github.com/kreuzberg-dev/tree-sitter-language-pack       ║
║    2. 下载所需语言的 parser 文件                                              ║
║    3. 将文件放置到缓存目录:                                                   ║
║       - Linux/macOS: ~/.cache/tree-sitter/                                   ║
║       - Windows: %LOCALAPPDATA%\\tree-sitter\\                                ║
║                                                                              ║
║  解决方案 3：配置代理（如需）                                                 ║
║    set HTTP_PROXY=http://your-proxy:port                                     ║
║    set HTTPS_PROXY=http://your-proxy:port                                    ║
║                                                                              ║
║  当前系统将自动降级使用 SentenceSplitter 进行文本切分                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""


def check_parser_cache(language: str) -> Optional[Path]:
    """
    检查本地是否存在 tree-sitter parser 缓存
    
    Args:
        language: 语言名称（如 'python', 'javascript'）
        
    Returns:
        如果找到缓存路径则返回 Path，否则返回 None
    """
    for cache_dir in TREE_SITTER_CACHE_DIRS:
        if cache_dir is None:
            continue
        if not cache_dir.exists():
            continue
        
        language_files = list(cache_dir.glob(f"*{language}*"))
        if language_files:
            return cache_dir
    
    return None


def timeout_handler(timeout_seconds: int):
    """
    超时装饰器，用于限制函数执行时间
    
    Args:
        timeout_seconds: 超时秒数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]
            exception = [None]
            
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout_seconds)
            
            if thread.is_alive():
                raise TimeoutError(
                    f"操作超时：{func.__name__} 执行超过 {timeout_seconds} 秒"
                )
            
            if exception[0] is not None:
                raise exception[0]
            
            return result[0]
        return wrapper
    return decorator


def init_code_splitter_with_timeout(
    language: str = "python",
    chunk_lines: int = 40,
    chunk_lines_overlap: int = 10,
    max_chars: int = 1500,
    timeout_seconds: int = 10
) -> Optional[CodeSplitter]:
    """
    初始化 CodeSplitter，带超时检测和缓存检查
    
    Args:
        language: 编程语言
        chunk_lines: 每个块的行数
        chunk_lines_overlap: 块之间的重叠行数
        max_chars: 最大字符数
        timeout_seconds: 超时秒数
        
    Returns:
        CodeSplitter 实例，如果失败则返回 None
    """
    print(f"\n{'='*60}")
    print("正在初始化 CodeSplitter...")
    print(f"目标语言: {language}")
    print(f"超时设置: {timeout_seconds} 秒")
    print(f"{'='*60}")
    
    cache_path = check_parser_cache(language)
    if cache_path:
        print(f"✓ 发现本地 parser 缓存: {cache_path}")
    else:
        print(f"⚠ 未发现本地 parser 缓存，将尝试在线下载...")
    
    def _init_splitter():
        from tree_sitter_language_pack import get_language, get_parser
        
        parser = get_parser(language)
        
        return CodeSplitter(
            language=language,
            chunk_lines=chunk_lines,
            chunk_lines_overlap=chunk_lines_overlap,
            max_chars=max_chars,
            parser=parser
        )
    
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_init_splitter)
            try:
                splitter = future.result(timeout=timeout_seconds)
                print(f"✓ CodeSplitter 初始化成功！")
                print(f"  - 切分模式: AST 感知")
                print(f"  - 块大小: {chunk_lines} 行")
                print(f"  - 重叠: {chunk_lines_overlap} 行")
                print(f"  - 最大字符: {max_chars}")
                return splitter
            except FuturesTimeoutError:
                raise TimeoutError(
                    f"tree-sitter parser 下载超时（{timeout_seconds}秒）"
                )
    except ImportError as e:
        print(f"\n✗ 导入失败: {e}")
        print("  原因: tree-sitter-language-pack 未安装")
        print(MANUAL_DOWNLOAD_GUIDE)
        return None
    except TimeoutError as e:
        print(f"\n✗ 超时错误: {e}")
        print("  原因: 网络连接问题或下载服务器响应缓慢")
        print(MANUAL_DOWNLOAD_GUIDE)
        return None
    except Exception as e:
        print(f"\n✗ 初始化失败: {type(e).__name__}: {e}")
        print("  原因: parser 文件损坏或版本不兼容")
        print(MANUAL_DOWNLOAD_GUIDE)
        return None


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
            llm: LLM 模型（可选）- 代码索引不使用
            embed_model: 嵌入模型（可选）
        """
        if embed_model:
            Settings.embed_model = embed_model
        else:
            # 使用本地 HuggingFace 模型作为默认嵌入模型
            # 方案 1: 尝试使用 HuggingFace 嵌入模型
            try:
                from llama_index.embeddings.huggingface import HuggingFaceEmbedding
                Settings.embed_model = HuggingFaceEmbedding(
                    model_name="BAAI/bge-small-zh-v1.5",
                    cache_folder=None,
                )
                print("已加载 HuggingFace 嵌入模型：bge-small-zh-v1.5")
            except ImportError:
                # 方案 2: 使用 LangChain 的 HuggingFace 嵌入
                try:
                    from llama_index.embeddings.langchain import LangchainEmbedding
                    from langchain_community.embeddings import HuggingFaceEmbeddings
                    Settings.embed_model = LangchainEmbedding(
                        HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
                    )
                    print("已加载 LangChain HuggingFace 嵌入模型：bge-small-zh-v1.5")
                except ImportError:
                    # 方案 3: 使用默认嵌入（可能需要 OpenAI API）
                    print("警告：无法加载 HuggingFace 嵌入模型，将使用默认配置")
        # 注意：代码索引不需要设置 llm，避免 langchain 兼容性问题
        
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
        supported_files_count = 0
        for ext, language in supported_extensions.items():
            code_files = list(self.codebase_dir.rglob(f"*{ext}"))
            supported_files_count += len(code_files)
            
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
        
        print(f"找到 {supported_files_count} 个支持的代码文件，成功加载 {len(documents)} 个")
        
        if not documents:
            print(f"警告：未在 {self.codebase_dir} 中找到支持的代码文件")
            return
        
        print(f"开始构建代码索引，共 {len(documents)} 个代码文件...")
        start_time = time.time()
        
        code_splitter = init_code_splitter_with_timeout(
            language="python",
            chunk_lines=40,
            chunk_lines_overlap=10,
            max_chars=1500,
            timeout_seconds=10
        )
        
        if code_splitter is None:
            print("\n" + "="*60)
            print("⚠ 降级提示：CodeSplitter 初始化失败")
            print("="*60)
            print("原因分析:")
            print("  1. tree-sitter parser 下载超时（网络问题）")
            print("  2. tree-sitter-language-pack 未正确安装")
            print("  3. parser 文件损坏或版本不兼容")
            print("\n解决方案:")
            print("  - 执行: pip install tree-sitter-language-pack")
            print("  - 或手动下载: https://github.com/kreuzberg-dev/tree-sitter-language-pack")
            print("\n当前状态:")
            print("  → 自动降级使用 SentenceSplitter 进行文本切分")
            print("  → 代码索引功能仍可正常使用，但切分效果可能不如 AST 感知模式")
            print("="*60 + "\n")
            
            from llama_index.core.node_parser import SentenceSplitter
            code_splitter = SentenceSplitter(chunk_size=1024, chunk_overlap=64)
            print("✓ 已切换到 SentenceSplitter 模式")
        
        # 创建 ChromaDB 向量存储
        print("正在初始化向量存储...")
        db_init_start = time.time()
        db = chromadb.PersistentClient(path=self.persist_dir)
        chroma_collection = db.get_or_create_collection("codebase")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        print(f"✓ 向量存储初始化完成 (耗时：{time.time() - db_init_start:.2f}秒)")
        
        # 分批次处理文档，添加进度显示
        print(f"正在处理 {len(documents)} 个代码文件...")
        batch_size = 5  # 每批处理 5 个文件
        all_nodes = []
        
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(documents) + batch_size - 1) // batch_size
            
            print(f"  处理批次 {batch_num}/{total_batches} (文件 {i+1}-{min(i+batch_size, len(documents))})...")
            batch_start = time.time()
            
            try:
                # 对每批文档进行切分和嵌入
                batch_index = VectorStoreIndex.from_documents(
                    batch_docs,
                    storage_context=storage_context,
                    transformations=[code_splitter],
                    show_progress=True
                )
                
                # 获取所有节点
                if hasattr(batch_index, '_docstore'):
                    nodes = list(batch_index._docstore.docs.values())
                    all_nodes.extend(nodes)
                
                batch_time = time.time() - batch_start
                print(f"  ✓ 批次 {batch_num} 完成 (耗时：{batch_time:.2f}秒，节点数：{len(nodes) if 'nodes' in locals() else 'N/A'})")
                
            except Exception as e:
                print(f"  ⚠ 批次 {batch_num} 处理失败：{e}")
                import traceback
                traceback.print_exc()
                # 继续处理下一批
                continue
        
        # 创建统一的索引
        print(f"正在创建统一索引...")
        index_start = time.time()
        
        try:
            self.index = VectorStoreIndex(
                nodes=all_nodes if all_nodes else None,
                storage_context=storage_context,
                embed_model=Settings.embed_model
            )
            
            print(f"✓ 索引创建完成 (耗时：{time.time() - index_start:.2f}秒)")
            
            # 创建查询引擎
            try:
                self.query_engine = self.index.as_query_engine(
                    similarity_top_k=5,
                    include_metadata=True
                )
            except Exception as e2:
                print(f"警告：查询引擎创建失败，使用简化配置：{e2}")
                # 回退到最简单的查询引擎
                from llama_index.core.query_engine import RetrieverQueryEngine
                retriever = self.index.as_retriever(similarity_top_k=5)
                self.query_engine = RetrieverQueryEngine(retriever=retriever)
            
            total_time = time.time() - start_time
            print(f"\n{'='*60}")
            print(f"✓ 代码索引构建完成！")
            print(f"  - 处理文件数：{len(documents)}")
            print(f"  - 总节点数：{len(all_nodes)}")
            print(f"  - 总耗时：{total_time:.2f}秒 ({total_time/60:.2f}分钟)")
            print(f"{'='*60}")
            
        except Exception as e:
            print(f"✗ 代码索引构建失败：{e}")
            import traceback
            traceback.print_exc()
    
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

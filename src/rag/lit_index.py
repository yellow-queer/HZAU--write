"""
文献知识库 RAG 索引模块

负责：
1. 解析 EndNote 导出的 .ris 文件，提取 Citation Keys 和元数据
2. 为文献 PDF 创建 LlamaIndex 向量索引
3. 提供文献检索接口
"""

import os
import re
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


def format_citation(metadata: Dict[str, Any]) -> str:
    authors = metadata.get('au', [])
    year = metadata.get('py', metadata.get('y1', ''))
    if not authors:
        return f"({'Unknown'} {year})" if year else "(Unknown)"
    is_chinese = any(re.search(r'[\u4e00-\u9fff]', name) for name in authors)
    if is_chinese:
        formatted_authors = []
        for name in authors:
            formatted_authors.append(name)
        if len(formatted_authors) == 1:
            author_str = formatted_authors[0]
        elif len(formatted_authors) == 2:
            author_str = formatted_authors[0] + '和' + formatted_authors[1]
        else:
            author_str = formatted_authors[0] + '等'
        return f'（{author_str} {year}）'
    else:
        surnames = []
        for name in authors:
            if ',' in name:
                surname = name.split(',')[0].strip()
            else:
                parts = name.strip().split()
                surname = parts[-1] if parts else name
            surnames.append(surname)
        if len(surnames) == 1:
            author_str = surnames[0]
        elif len(surnames) == 2:
            author_str = surnames[0] + ' and ' + surnames[1]
        else:
            author_str = surnames[0] + ' et al'
        return f'({author_str} {year})'


class LiteratureIndex:
    """文献知识库索引"""
    
    def __init__(self, literature_dir: str, persist_dir: str = ".chroma_literature"):
        """
        初始化文献索引
        
        Args:
            literature_dir: 文献目录路径（包含 PDF 和 .ris 文件）
            persist_dir: ChromaDB 持久化目录
        """
        self.literature_dir = Path(literature_dir)
        self.persist_dir = persist_dir
        self.citation_keys: List[str] = []
        self.ref_metadata: Dict[str, Dict[str, Any]] = {}
        self.index: Optional[VectorStoreIndex] = None
        self.query_engine = None
        
    def parse_ris_file(self, ris_file_path: Optional[str] = None) -> List[str]:
        """
        解析 EndNote 导出的 .ris 文件，提取所有 Citation Keys 和元数据
        
        RIS 格式说明：
        - TY: 类型 (JOUR, BOOK, CHAP, CONF, THES 等)
        - AU: 作者 (可多条)
        - TI: 标题
        - AB: 摘要
        - JO/J1/JF: 期刊名
        - PY/Y1: 出版年
        - VL: 卷
        - IS: 期
        - SP: 起始页
        - EP: 结束页
        - DO: DOI
        - UR: URL
        - ID: EndNote Citation Key (自定义标签)
        - ER: 记录结束标记
        
        Args:
            ris_file_path: .ris 文件路径，如果为 None 则自动查找 literature_dir 中的 .ris 文件
            
        Returns:
            Citation Keys 列表
        """
        if ris_file_path is None:
            ris_files = list(self.literature_dir.glob("*.ris"))
            if not ris_files:
                print(f"警告：未在 {self.literature_dir} 中找到 .ris 文件")
                return []
            ris_file_path = ris_files[0]
        
        ris_path = Path(ris_file_path)
        if not ris_path.exists():
            raise FileNotFoundError(f".ris 文件不存在：{ris_file_path}")
        
        with open(ris_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.citation_keys = []
        self.ref_metadata = {}
        
        # 按 ER 分割每条记录
        records = re.split(r'^ER\s*-\s*$', content, flags=re.MULTILINE)
        
        for record in records:
            record = record.strip()
            if not record:
                continue
            
            metadata = self._parse_ris_record(record)
            if not metadata:
                continue
            
            citation_key = metadata.get('id', '')
            if not citation_key:
                # 如果没有 ID 字段，自动生成：作者年份
                authors = metadata.get('au', [])
                year = metadata.get('py', metadata.get('y1', ''))
                if authors and year:
                    first_author = authors[0].split(',')[0].strip().lower() if authors else 'unknown'
                    first_author = re.sub(r'[^a-z]', '', first_author)
                    citation_key = f"{first_author}{year}"
                else:
                    citation_key = f"ref{len(self.citation_keys) + 1}"
            
            metadata['key'] = citation_key
            self.citation_keys.append(citation_key)
            self.ref_metadata[citation_key] = metadata
        
        print(f"从 {ris_path.name} 解析了 {len(self.citation_keys)} 篇文献")
        return self.citation_keys
    
    def _parse_ris_record(self, record: str) -> Dict[str, Any]:
        """
        解析单条 RIS 记录
        
        Args:
            record: 单条 RIS 记录文本
            
        Returns:
            元数据字典
        """
        metadata: Dict[str, Any] = {}
        current_tag = None
        current_value = ""
        
        for line in record.split('\n'):
            line = line.rstrip()
            if not line:
                continue
            
            # RIS 标签行格式：TAG  - VALUE (标签2-3字符，6个空格，短横线，空格，值)
            tag_match = re.match(r'^([A-Z][A-Z0-9])\s*-\s*(.*)', line)
            if tag_match:
                # 保存上一个标签的值
                if current_tag:
                    self._add_tag_value(metadata, current_tag, current_value.strip())
                
                current_tag = tag_match.group(1).upper()
                current_value = tag_match.group(2)
            else:
                # 续行
                if current_tag:
                    current_value += " " + line
        
        # 保存最后一个标签
        if current_tag:
            self._add_tag_value(metadata, current_tag, current_value.strip())
        
        return metadata
    
    def _add_tag_value(self, metadata: Dict[str, Any], tag: str, value: str):
        """
        将 RIS 标签值添加到元数据字典
        
        Args:
            metadata: 元数据字典
            tag: RIS 标签
            value: 标签值
        """
        tag_lower = tag.lower()
        
        # 多值字段（作者、关键词等）
        multi_value_tags = {'AU', 'A1', 'A2', 'A3', 'A4', 'KW', 'N1'}
        
        if tag in multi_value_tags:
            if tag_lower not in metadata:
                metadata[tag_lower] = []
            metadata[tag_lower].append(value)
        else:
            # 期刊名映射
            if tag == 'JF' and 'jo' not in metadata and 'j1' not in metadata:
                metadata['jo'] = value
            elif tag == 'J1' and 'jo' not in metadata:
                metadata['jo'] = value
            else:
                metadata[tag_lower] = value
    
    def build_index(self, llm=None, embed_model=None):
        """
        构建文献向量索引
        
        Args:
            llm: LLM 模型（可选）
            embed_model: 嵌入模型（可选）
        """
        if embed_model:
            Settings.embed_model = embed_model
        else:
            # 使用本地 HuggingFace 模型作为默认嵌入模型
            try:
                from llama_index.embeddings.huggingface import HuggingFaceEmbedding
                Settings.embed_model = HuggingFaceEmbedding(
                    model_name="BAAI/bge-small-zh-v1.5",
                    cache_folder=None,
                )
                print("已加载 HuggingFace 嵌入模型：bge-small-zh-v1.5")
            except Exception as e:
                print(f"警告：无法加载 HuggingFace 嵌入模型，将使用默认配置：{e}")
        if llm:
            Settings.llm = llm
        
        documents = []
        
        # 加载 PDF 文件
        pdf_files = list(self.literature_dir.glob("*.pdf"))
        pdf_subdir = self.literature_dir / "pdf"
        if pdf_subdir.exists():
            pdf_files.extend(pdf_subdir.glob("*.pdf"))
        for pdf_file in pdf_files:
            try:
                from llama_index.readers.file import PDFReader
                reader = PDFReader()
                pdf_docs = reader.load_data(file=pdf_file)
                
                for doc in pdf_docs:
                    doc.metadata['source'] = pdf_file.name
                    documents.append(doc)
                
                print(f"加载 PDF: {pdf_file.name}")
            except Exception as e:
                print(f"加载 PDF 失败 {pdf_file.name}: {e}")
        
        # 添加 RIS/XML 元数据作为文档
        for key, metadata in self.ref_metadata.items():
            title = metadata.get('ti', 'Unknown Title')
            abstract = metadata.get('ab', '')
            authors = metadata.get('au', [])
            year = metadata.get('py', metadata.get('y1', ''))
            journal = metadata.get('jo', '')
            
            content = f"Title: {title}\n"
            if authors:
                if isinstance(authors, list):
                    content += f"Authors: {'; '.join(authors)}\n"
                else:
                    content += f"Authors: {authors}\n"
            if year:
                content += f"Year: {year}\n"
            if journal:
                content += f"Journal: {journal}\n"
            if abstract:
                content += f"Abstract: {abstract}\n"
            
            doc = Document(
                text=content,
                metadata={
                    'source': f'{key}.ris',
                    'citation_key': key,
                    'type': 'ris_metadata'
                }
            )
            documents.append(doc)
        
        if not documents:
            print("警告：没有找到任何文献文档")
            return
        
        print(f"开始构建文献索引，共 {len(documents)} 个文档...")
        
        # 创建 ChromaDB 向量存储
        db = chromadb.PersistentClient(path=self.persist_dir)
        chroma_collection = db.get_or_create_collection("literature")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # 创建索引
        try:
            node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=64)
            self.index = VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context,
                node_parser=node_parser
            )
            
            # 创建查询引擎
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=5,
                include_metadata=True
            )
            
            print(f"文献索引构建完成，共 {len(documents)} 个文档")
        except Exception as e:
            print(f"文献索引构建失败：{e}")
            import traceback
            traceback.print_exc()
    
    def query(self, query_str: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        查询文献索引
        
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
    
    def get_valid_citation_keys(self) -> List[str]:
        """获取所有合法的 Citation Keys"""
        return self.citation_keys.copy()
    
    def get_ref_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """获取指定 Citation Key 的元数据"""
        return self.ref_metadata.get(key)

    def generate_citation_texts(self) -> Dict[str, str]:
        result = {}
        for key, metadata in self.ref_metadata.items():
            result[key] = format_citation(metadata)
        return result

    @staticmethod
    def _extract_style_text(element) -> str:
        if element is None:
            return ""
        texts = []
        for style_el in element.iter("style"):
            if style_el.text:
                texts.append(style_el.text)
        return "".join(texts).strip()

    def parse_endnote_xml(self, xml_file_path=None):
        import xml.etree.ElementTree as ET

        if xml_file_path is None:
            xml_files = list(self.literature_dir.glob("*.xml"))
            if not xml_files:
                print(f"警告：未在 {self.literature_dir} 中找到 .xml 文件")
                return []
            xml_file_path = xml_files[0]

        xml_path = Path(xml_file_path)
        if not xml_path.exists():
            raise FileNotFoundError(f".xml 文件不存在：{xml_file_path}")

        tree = ET.parse(xml_path)
        root = tree.getroot()
        records = root.findall(".//record")

        new_keys = []

        for record in records:
            metadata = {}

            rec_num = self._extract_style_text(record.find("rec-number"))
            if not rec_num:
                rec_num = record.findtext("rec-number", "").strip()
            citation_key = f"ref_{rec_num}" if rec_num else f"ref{len(self.citation_keys) + len(new_keys) + 1}"

            ref_type_el = record.find("ref-type")
            if ref_type_el is not None:
                metadata["ty"] = ref_type_el.get("name", "")

            authors_el = record.find(".//contributors/authors")
            if authors_el is not None:
                au_list = []
                for author_el in authors_el.findall("author"):
                    author_text = self._extract_style_text(author_el)
                    if author_text:
                        au_list.append(author_text)
                if au_list:
                    metadata["au"] = au_list

            title_el = record.find(".//titles/title")
            title_text = self._extract_style_text(title_el)
            if title_text:
                metadata["ti"] = title_text

            sec_title_el = record.find(".//titles/secondary-title")
            sec_title_text = self._extract_style_text(sec_title_el)

            periodical_el = record.find(".//periodical/full-title")
            periodical_text = self._extract_style_text(periodical_el)

            if periodical_text:
                metadata["jo"] = periodical_text
            elif sec_title_text:
                metadata["jo"] = sec_title_text

            year_el = record.find(".//dates/year")
            year_text = self._extract_style_text(year_el)
            if year_text:
                metadata["py"] = year_text

            abstract_el = record.find("abstract")
            abstract_text = self._extract_style_text(abstract_el)
            if abstract_text:
                metadata["ab"] = abstract_text

            keywords_el = record.find(".//keywords")
            if keywords_el is not None:
                kw_list = []
                for kw_el in keywords_el.findall("keyword"):
                    kw_text = self._extract_style_text(kw_el)
                    if kw_text:
                        kw_list.append(kw_text)
                if kw_list:
                    metadata["kw"] = kw_list

            vol_el = record.find("volume")
            vol_text = self._extract_style_text(vol_el)
            if vol_text:
                metadata["vl"] = vol_text

            num_el = record.find("number")
            num_text = self._extract_style_text(num_el)
            if num_text:
                metadata["is"] = num_text

            pages_el = record.find("pages")
            pages_text = self._extract_style_text(pages_el)
            if pages_text:
                metadata["sp"] = pages_text

            pub_el = record.find("publisher")
            pub_text = self._extract_style_text(pub_el)
            if pub_text:
                metadata["pb"] = pub_text

            doi_el = record.find("electronic-resource-num")
            doi_text = self._extract_style_text(doi_el)
            if doi_text:
                metadata["do"] = doi_text

            if not metadata.get("ti"):
                continue

            metadata["key"] = citation_key
            new_keys.append(citation_key)
            self.citation_keys.append(citation_key)
            self.ref_metadata[citation_key] = metadata

        print(f"从 {xml_path.name} 解析了 {len(new_keys)} 篇文献")
        return new_keys

    def parse_endnote_txt(self, txt_file_path: Optional[str] = None) -> List[str]:
        if txt_file_path is None:
            txt_files = list(self.literature_dir.glob("*.txt"))
            if not txt_files:
                print(f"警告：未在 {self.literature_dir} 中找到 .txt 文件")
                return []
            txt_file_path = txt_files[0]

        txt_path = Path(txt_file_path)
        if not txt_path.exists():
            raise FileNotFoundError(f".txt 文件不存在：{txt_file_path}")

        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()

        new_keys = []

        records = re.split(r'^ER\s*-\s*$', content, flags=re.MULTILINE)

        for record in records:
            record = record.strip()
            if not record:
                continue

            metadata = self._parse_ris_record(record)
            if not metadata:
                continue

            citation_key = metadata.get('id', '')
            if not citation_key:
                authors = metadata.get('au', [])
                year = metadata.get('py', metadata.get('y1', ''))
                if authors and year:
                    first_author = authors[0].split(',')[0].strip().lower() if authors else 'unknown'
                    first_author = re.sub(r'[^a-z]', '', first_author)
                    citation_key = f"{first_author}{year}"
                else:
                    citation_key = f"ref{len(self.citation_keys) + len(new_keys) + 1}"

            metadata['key'] = citation_key
            new_keys.append(citation_key)
            self.citation_keys.append(citation_key)
            self.ref_metadata[citation_key] = metadata

        print(f"从 {txt_path.name} 解析了 {len(new_keys)} 篇文献")
        return new_keys

    def parse_literature_files(self) -> List[str]:
        all_keys = []

        xml_files = list(self.literature_dir.glob("*.xml"))
        if xml_files:
            xml_keys = self.parse_endnote_xml()
            all_keys.extend(xml_keys)

        ris_files = list(self.literature_dir.glob("*.ris"))
        if ris_files:
            ris_keys = self.parse_ris_file()
            all_keys.extend(ris_keys)

        txt_files = list(self.literature_dir.glob("*.txt"))
        if txt_files:
            txt_keys = self.parse_endnote_txt()
            all_keys.extend(txt_keys)

        print(f"共解析 {len(all_keys)} 篇文献（XML: {len(xml_files)} 个文件, RIS: {len(ris_files)} 个文件, TXT: {len(txt_files)} 个文件）")
        return all_keys
    


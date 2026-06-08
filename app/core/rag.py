from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import ZhipuAIEmbeddings
import os
class RAGManager:
    def __init__(self, user_id: int, session_id: int):
        self.user_id = user_id
        self.session_id = session_id
        # 每个用户/会话有独立的向量库
        self.vectorstore_path = f"vectorstores/user_{user_id}_session_{session_id}"
        self.embeddings = ZhipuAIEmbeddings(
            model="embedding-3",
            api_key="156332acd1214bd2bd2470bab4447382.xDTdXn4knyZXX9hK"
        )

    def process_document(self, file_path: str) -> bool:
            """处理文档：加载 → 切分 → 向量化 → 存储"""
            # 1. 根据文件类型选择加载器
            if file_path.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
            else:
                loader = TextLoader(file_path, encoding='utf-8')

            documents = loader.load()
            # 2. 切分文本
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                separators=["\n\n", "\n", "。", "！", "？", " ", ""]
            )
            chunks = splitter.split_documents(documents)

            # 3. 存入向量库
            if os.path.exists(self.vectorstore_path):
                # 已有向量库，追加
                vectorstore = FAISS.load_local(
                    self.vectorstore_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                vectorstore.add_documents(chunks)
            else:
                # 新建向量库
                vectorstore = FAISS.from_documents(chunks, self.embeddings)

            vectorstore.save_local(self.vectorstore_path)
            return True

    def search(self, query: str, top_k: int = 3) -> str:
            """根据问题检索相关文档片段"""
            if not os.path.exists(self.vectorstore_path):
                return "暂无文档，请先上传文档"

            vectorstore = FAISS.load_local(
                self.vectorstore_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )

            docs = vectorstore.similarity_search(query, k=top_k)
            return "\n\n".join([doc.page_content for doc in docs])
# Warning:Let you always trust youself.
# lesson:vipPython
# user:April 
# starting time:2026/6/5 18:35
from langchain_openai import ChatOpenAI #大脑
from langchain.tools import tool #工具
from langgraph.prebuilt import create_react_agent #控制器
from app.core.rag import RAGManager
import os
def create_agent(db, user_id: int, session_id: int):
    # 工具一：查询对话历史
    @tool
    def get_history() -> str:
        ##下面这一行就是docstring，给LLM看的
        """查询当前用户在当前会话里的历史对话记录"""
        from app.models.conversation import Conversation
        records = db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.session_id == session_id
        ).order_by(Conversation.id).all()

        if not records:
            return "暂无历史记录"

        result = []
        for r in records:
            result.append(f"{r.role}: {r.content}")
        return "\n".join(result)

    # 工具二：获取当前时间
    @tool
    def get_current_time() -> str:
        """获取当前日期和时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")

    @tool
    def search_documents(query: str) -> str:
        """根据用户问题检索上传的文档内容"""
        rag = RAGManager(user_id, session_id)  # 通过闭包获取
        return rag.search(query)

    # 初始化 LLM
    llm = ChatOpenAI(
        model="deepseek-chat",
        openai_api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
        openai_api_base="https://api.deepseek.com"
    )

    # ========== 系统提示词 ==========
    system_prompt = """你是一个智能助手，可以：
    1. 查询对话历史了解上下文
    2. 获取当前时间
    3. 搜索网络信息
    4. 检索用户上传的文档内容

    当用户询问文档相关内容时，优先使用 search_documents 工具检索。
    回答时要基于检索到的文档内容，不要编造信息。
    如果检索不到相关内容，请如实告知用户。
    """
    tools = [get_history, get_current_time,search_documents]
    agent = create_react_agent(llm, tools)
    return agent
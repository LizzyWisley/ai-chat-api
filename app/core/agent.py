# Warning:Let you always trust youself.
# lesson:vipPython
# user:April 
# starting time:2026/6/5 18:35
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
import os


def create_agent(db, user_id: int, session_id: int):
    # 工具一：查询对话历史
    @tool
    def get_history() -> str:
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

    # 初始化 LLM
    llm = ChatOpenAI(
        model="deepseek-chat",
        openai_api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
        openai_api_base="https://api.deepseek.com"
    )

    tools = [get_history, get_current_time]
    agent = create_react_agent(llm, tools)
    return agent
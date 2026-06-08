# AI Chat API - 基于 FastAPI 的 AI Agent 对话系统

基于 FastAPI + LangGraph 构建的 AI 对话系统，集成 ReAct Agent 实现工具调用能力，
支持对话历史查询、时间获取、网络搜索等功能。

## 技术栈

- **后端框架**: FastAPI + Uvicorn
- **数据库**: SQLite + SQLAlchemy
- **AI 框架**: LangGraph + LangChain
- **LLM**: DeepSeek API (OpenAI 兼容接口)
- **认证**: JWT + OAuth2

## 核心功能

- [x] JWT 用户认证与 RBAC 权限控制
- [x] 多用户会话隔离与历史持久化
- [x] ReAct Agent 工具调用（3个工具）
  - `get_history` - 对话历史查询
  - `get_current_time` - 当前时间获取
  - `search_web` - 网络搜索（Serper.dev）
- [x] 流式对话响应
- [x] 自动会话标题生成

## 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/LizzyWisley/ai-chat-api.git
cd ai-chat-api

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 DeepSeek API Key

# 4. 启动服务
uvicorn app.main:app --reload
```

## API 文档

启动后访问: http://localhost:8000/docs

## 项目结构
app/ ├── core/ # Agent 核心逻辑 + 安全配置 ├── models/ # 数据库模型 ├── routers/ # API 路由 ├── database.py # 数据库连接 └── main.py # 入口文件

## 技术亮点

- **闭包工厂模式**: `create_agent()` 为每个用户创建独立 Agent 实例，工具内部自动绑定 `user_id`/`session_id`，实现多用户数据隔离
- **ReAct 推理循环**: LLM 分析用户意图 → 选择并调用工具 → 获取 Observation → 生成最终回复
- **@tool 装饰器**: 自动提取函数元数据生成 JSON Schema，供 LLM 决策调用

## 联系方式

- GitHub: [@LizzyWisley](https://github.com/LizzyWisley)
- 邮箱: 3025415908@qq.com


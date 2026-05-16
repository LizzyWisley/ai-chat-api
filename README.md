# AI 对话后端系统

基于 FastAPI 开发的带用户认证的 AI 对话后端服务，接入 DeepSeek 大模型。

## 技术栈
- FastAPI + SQLAlchemy + SQLite
- JWT 身份认证
- bcrypt 密码加密
- DeepSeek API

## 接口列表
| 接口 | 方法 | 说明 |
|------|------|------|
| /register | POST | 用户注册 |
| /login | POST | 用户登录，返回 JWT Token |
| /user/me | GET | 获取当前登录用户信息 |
| /chat | POST | 发送消息，获取 AI 回复 |
| /chat/history | GET | 查询当前用户的历史对话 |

## 项目结构
app/
├── core/         # 核心工具（加密、token）
├── models/       # 数据库模型
├── routers/      # 接口路由
├── schemas/      # 数据格式定义
├── database.py   # 数据库连接
└── main.py       # 项目入口
## 启动方式
```bash
uvicorn app.main:app --reload --port 8001
```
访问 http://127.0.0.1:8001/docs 查看接口文档

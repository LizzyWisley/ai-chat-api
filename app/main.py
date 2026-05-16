from fastapi import FastAPI, Depends, HTTPException, status
from app.routers import auth
app = FastAPI(title="用户登录系统")
app.include_router(auth.router)
from app.routers import auth, chat
app.include_router(chat.router)



# Warning:Let you always trust youself.
# lesson:vipPython
# user:April 
# starting time:2026/6/8 10:30
from app.core.rag import RAGManager
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.database import get_db
from app.core.security import oauth2_scheme, SECRET_KEY, ALGORITHM
from fastapi import Form
import os
os.makedirs("uploads", exist_ok=True)
router = APIRouter()

@router.post("/documents/upload")
async def upload_document(
        file: UploadFile = File(...),
        session_id: int = Form(...),
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    # 解析token获取用户
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="无效凭证")

    from app.models.user import User
    user = db.query(User).filter(User.email == email).first()

    # 保存文件
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # 处理文档
    rag = RAGManager(user.id, session_id)
    success = rag.process_document(file_path)

    # 记录到数据库...

    return {"message": "文档处理完成" if success else "处理失败"}
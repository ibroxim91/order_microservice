import bcrypt
from fastapi import  APIRouter
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from app.auth.tokens import create_access_token, verify_access_token
from app.models.user import User
from fastapi import HTTPException, Depends, status
from app.db import get_db
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.get_user import get_current_user
from app.schemas.auth_schema import Token,  UserResponse, UserAuth
from app.crud.user_crud import personal_get_user_data, create_user
from app.schemas.auth_schema import UserRegister


auth_router = APIRouter()

__all__ = ["auth_router"]

# Зависимость OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="access")




# Маршрут для получения токена доступа
@auth_router.post("/access", response_model=Token)
async def login_for_access_token(user: UserAuth, db: Session = Depends(get_db)):
    """
    Login for access token.
    """
    user_db = await db.execute(select(User).where(User.username == user.username))
    user_db = user_db.scalar_one_or_none()
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    if not bcrypt.checkpw(user.password.encode('utf-8'), hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")


# # Маршрут для обновления токена
@auth_router.post("/refresh", response_model=Token)
def refresh_token(token: str = Depends(oauth2_scheme)):
    """
    Refresh access token.
    """
    try:
        payload = verify_access_token(token)
        pin_code = payload.get("sub")
        new_access_token = create_access_token(data={"sub": pin_code})
        return {"access_token": new_access_token, "token_type": "bearer"}

    except HTTPException as e:
        raise e

@auth_router.get("/me", response_model=UserResponse)
async def get_user_data(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    """
    Get user data.
    """
    user_data = await personal_get_user_data(db, user.id)
    return user_data




@auth_router.post("/register", response_model=UserResponse)
async def register_user(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.
    """
    try:
        user = await create_user(db, payload.username, payload.email, payload.password)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

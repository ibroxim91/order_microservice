import os
from app.schemas.auth_schema import UserSchema, UserResponse
from dotenv import load_dotenv
from fastapi import HTTPException, Header, status, Depends
from sqlalchemy import select
from app.auth.tokens import verify_access_token

from app.models.user import User as UserModel
from app.db import get_db
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import  get_db
from fastapi import HTTPException, status, Depends, Request

from app.config import REDIS_CLIENT as redis 

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'secret11223344')
ALGORITHM = os.getenv('ALGORITHM', 'HS256')

import json


async def get_current_user(
    request: Request,
    authorization: str = Header(default=None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
    only_token: bool = False
):

    # Token tekshiruvi
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not provided or invalid format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ")[1]

    # Check redis cache
    cache_key = f"user:{token}"
    cached_user = await redis.get(cache_key)
    if cached_user:
        user_data = json.loads(cached_user)
        return UserResponse(**user_data) 


    try:
        payload = verify_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # DB query
    query = await db.execute(
        select(UserModel).where(UserModel.username == username)
    )
    user = query.scalars().first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Convert user to UserSchema
    user_schema = UserResponse.from_orm(user)
    await redis.set(cache_key, user_schema.json())

    return user


async def get_admin_user(current_user: UserModel = Depends(get_current_user)):
    if current_user.role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have a role assigned",
        )

   

    if  current_user.role not in ["admin", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    return current_user




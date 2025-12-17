from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload
from app.models.user import User  # Import the User model
from app.schemas.auth_schema import UserResponse # Import the UserResponse schema
from sqlalchemy import select


async def create_user(db: AsyncSession, username: str, email: str, password: str) -> User:
    # Tekshirish: username yoki email band emasligini aniqlash
    res = await db.execute(select(User).where(User.username == username))
    if res.scalar_one_or_none():
        raise ValueError("Username already exists")

    res = await db.execute(select(User).where(User.email == email))
    if res.scalar_one_or_none():
        raise ValueError("Email already exists")
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    user = User(username=username, email=email)
    user.set_password(password)  # parolni hash qilish
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user



async def personal_get_user_data(db: AsyncSession, user_id: int) -> UserResponse:
    result = await db.execute(
        select(User)
        .filter(User.id == user_id)
        )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    first_name=user.first_name if user.first_name else None,
                    last_name=user.last_name if user.last_name else None
                    
                    )

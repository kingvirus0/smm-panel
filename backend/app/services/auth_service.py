import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import UnauthorizedError, SMMPanelException


def generate_referral_code() -> str:
    return uuid.uuid4().hex[:8].upper()


async def register_user(db: AsyncSession, email: str, username: str, password: str, referral_code: str | None = None) -> User:
    existing = await db.execute(select(User).where((User.email == email) | (User.username == username)))
    if existing.scalar_one_or_none():
        raise SMMPanelException("Email or username already exists")
    
    referred_by = None
    if referral_code:
        referrer = await db.execute(select(User).where(User.referral_code == referral_code))
        referrer_user = referrer.scalar_one_or_none()
        if referrer_user:
            referred_by = referrer_user.id

    user = User(
        email=email,
        username=username,
        hashed_password=get_password_hash(password),
        referral_code=generate_referral_code(),
        referred_by=referred_by,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise UnauthorizedError("Invalid email or password")
    if user.is_banned:
        raise UnauthorizedError("Account is banned")
    return user


def create_token_pair(user: User) -> dict:
    access = create_access_token({"sub": user.id, "role": user.role})
    refresh = create_refresh_token({"sub": user.id})
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> dict:
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise UnauthorizedError("Invalid refresh token")
    
    result = await db.execute(select(User).where(User.id == payload["sub"]))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or inactive")
    
    return create_token_pair(user)

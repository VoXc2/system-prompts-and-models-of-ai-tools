"""API dependencies - authentication, database session, etc."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings
from app.database import async_session

settings = get_settings()
security = HTTPBearer(auto_error=False)


async def get_db():
    """Get async database session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Validate JWT token and return current user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="بيانات الدخول مطلوبة",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id: str = payload.get("sub")
        tenant_id: str = payload.get("tenant_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="توكن غير صالح",
            )
        return {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "email": payload.get("email"),
            "role": payload.get("role"),
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توكن غير صالح أو منتهي",
        )


async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
):
    """Get current active user (not disabled)."""
    return current_user


async def require_role(required_roles: list):
    """Dependency to require specific roles."""
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="صلاحيات غير كافية",
            )
        return current_user
    return role_checker

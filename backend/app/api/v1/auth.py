from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_db
from backend.app.core.config import settings
from backend.app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)
from backend.app.models.models import RefreshToken, User
from backend.app.schemas.schemas import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from backend.app.services.audit import write_audit

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    exists = db.scalar(select(User).where(User.email == payload.email))
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already registered")
    user = User(email=payload.email, password_hash=hash_password(payload.password), household_name=payload.household_name)
    db.add(user)
    db.flush()
    refresh = create_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh),
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_days),
        )
    )
    write_audit(db, user.id, "auth.register", "user", user.id)
    db.commit()
    return TokenResponse(access_token=create_access_token(user.id), refresh_token=refresh)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email, User.deleted_at.is_(None)))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    refresh = create_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh),
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_days),
        )
    )
    write_audit(db, user.id, "auth.login", "user", user.id)
    db.commit()
    return TokenResponse(access_token=create_access_token(user.id), refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    token_hash = hash_token(payload.refresh_token)
    token = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash, RefreshToken.revoked.is_(False)))
    if not token or token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid refresh token")
    token.revoked = True
    new_refresh = create_refresh_token()
    db.add(
        RefreshToken(
            user_id=token.user_id,
            token_hash=hash_token(new_refresh),
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_days),
        )
    )
    write_audit(db, token.user_id, "auth.refresh", "refresh_token", token.id)
    db.commit()
    return TokenResponse(access_token=create_access_token(token.user_id), refresh_token=new_refresh)


@router.post("/logout")
def logout(payload: RefreshRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    token = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_token(payload.refresh_token), RefreshToken.user_id == user.id))
    if token:
        token.revoked = True
        write_audit(db, user.id, "auth.logout", "refresh_token", token.id)
        db.commit()
    return {"ok": True}

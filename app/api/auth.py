from fastapi import APIRouter,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    TokenResponse,UserLogin,UserRegister,UserResponse
)
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)

router=APIRouter(prefix="/auth",tags=["Authentication"])







@router.post("/register",
             response_model=UserResponse,
             status_code=status.HTTP_201_CREATED,
)
def register_user(
    data:UserRegister,
    db:Session=Depends(get_db),

):
    email=str(data.email).lower()
    existing_user=db.scalar(
        select(User).where(User.email==email)

    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )
    user=User(
        name=data.name,
        email=email,
        password_hash=hash_password(data.password),
        role="passenger",
    )

    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not register user. The email may already exist.",
        )

    return user






@router.post("/login", response_model=TokenResponse)
def login_user(
    data: UserLogin,
    db: Session = Depends(get_db),
):
    email = str(data.email).lower()

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if not user or not verify_password(
        data.password, user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(
        access_token=create_access_token(user.id)
    )






@router.post("/token", response_model=TokenResponse)
def login_form(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    email = form.username.lower()

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if not user or not verify_password(
        form.password, user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(
        access_token=create_access_token(user.id)
    )

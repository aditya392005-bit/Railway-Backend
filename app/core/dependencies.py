from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.security import settings
from app.database import get_db
from app.models.user import User
import jwt

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user(
        token:str=Depends(oauth2_scheme),
        db:Session=Depends(get_db),
)->User:
    credentials_error=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate":"Bearer"},
    )
    try:
        payload=jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id=int(payload["sub"])
    except (InvalidTokenError,KeyError,TypeError,ValueError):
        raise credentials_error
    user =db.get(User,user_id)
    if user is None:
        raise credentials_error
    return user

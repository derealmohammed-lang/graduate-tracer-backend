from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import ChangePasswordRequest, UserMeOut, UserMeUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserMeOut)
def get_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_service.build_user_me(db, user)


@router.patch("/me", response_model=UserMeOut)
def update_me(payload: UserMeUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_service.update_user_me(db, user, payload)


@router.post("/me/change-password", status_code=status.HTTP_200_OK)
def change_password(payload: ChangePasswordRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    user.password_hash = hash_password(payload.new_password)
    db.commit()
    return {"message": "Password updated successfully"}


@router.post("/me/profile-photo", response_model=UserMeOut)
async def upload_profile_photo(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await user_service.save_profile_photo(db, user, file)

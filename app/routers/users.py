from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_role
from app.models import Role, User
from app.schemas import RoleUpdate, UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(Role.admin)),
):
    return db.scalars(select(User).order_by(User.id)).all()


@router.patch("/{user_id}/role", response_model=UserOut)
def set_role(
    user_id: int,
    data: RoleUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(Role.admin)),
):
    if user_id == admin.id:
        # zaštita da admin slučajno ne ukine sam sebe
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Ne možeš mijenjati svoju ulogu")

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Korisnik ne postoji")

    user.role = data.role
    db.commit()
    db.refresh(user)
    return user
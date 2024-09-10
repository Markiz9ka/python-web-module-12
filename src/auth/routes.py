import fastapi
import fastapi.security
import database

import auth.exceptions
import auth.service
import auth.models
import auth.schemas

auth_service = auth.service.Auth()
router = fastapi.APIRouter(prefix='/auth', tags=["auth"])

@router.post(
    "/signup",
    status_code=fastapi.status.HTTP_201_CREATED
)
async def signup(
    body: auth.schemas.User,
    db = fastapi.Depends(database.get_database)
) -> auth.schemas.UserDb:
    user = db.query(auth.models.User).filter(auth.models.User.username==body.username).first()
    if user is not None:
        raise fastapi.HTTPException(
            fastapi.status.HTTP_409_CONFLICT,
            detail="Account already exists"
        )

    hashed_password = auth_service.hash_password(body.password)

    new_user = auth.models.User(
        username=body.username,
        hash_password=hashed_password
    )

    db.add(new_user)
    db.commit()

    return new_user


@router.post("/login")
async def login(
    body: fastapi.security.OAuth2PasswordRequestForm = fastapi.Depends(),
    db = fastapi.Depends(database.get_database)
) -> auth.schemas.Token:
    user = db.query(auth.models.User).filter(auth.models.User.username==body.username).first()
    if user is None:
        raise auth.exceptions.AuthException("no such user")

    verification = auth_service.verify_password(body.password, user.hash_password)
    if not verification:
        raise auth.exceptions.AuthException("incorrect credentials")

    refresh_token = await auth_service.create_refresh_token(payload={"sub": body.username})
    access_token = await auth_service.create_access_token(payload={"sub": body.username})

    user.refresh_token = refresh_token
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    }


@router.post("/logout")
async def logout(
    user = fastapi.Depends(auth_service.get_user),
    db = fastapi.Depends(database.get_database)
) -> auth.schemas.LogoutResponse:
    user.refresh_token = None
    db.commit()

    return {"result": "Success"}

from fastapi import APIRouter, Request, Response, HTTPException,status
from app.controllers import auth_controller
from app.models.user import SignUpRequest, LoginRequest
from pymongo.errors import DuplicateKeyError
from bson import ObjectId


router = APIRouter()

@router.post("/auth/signup")
async def signup(request: Request, data: SignUpRequest):
    db = request.app.mongodb
    email = data.email
    name = data.name
    password = data.password
    confirm_password = data.confirm_password

    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    try:
        # Create the user
        await auth_controller.create_user(name, email, password, db)
        return {"message": "User created successfully"}
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/auth/login")
async def login(request: Request, response: Response, data: LoginRequest):
    try:
        db = request.app.mongodb

        email = data.email
        password = data.password

        # Check if user exists
        user = await auth_controller.get_user_by_email(email, db)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email")

        # Verify password
        if not auth_controller.verify_password(password, user.get("hashed_password", "")):
            raise HTTPException(status_code=401, detail="Invalid password")

        # Create token
        token = auth_controller.create_access_token({"sub": str(user["_id"])})

        # Set secure cookie
        response.set_cookie(
            key="token",
            value=token,
            httponly=True,
            max_age=3600,
            secure=False,
            samesite="none"
        )
        return {"message": "Login successful"}

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        # Catch unexpected errors (e.g., DB connection issues, logic errors)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/auth/verify")
async def me(request: Request):
    db = request.app.mongodb

    # Check for token in cookies
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Not logged in. Token missing from cookies.")

    # Decode the token
    try:
        user_id = auth_controller.decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Failed to decode token.")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    # Validate user ID format
    try:
        user_obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format in token.")

    # Check if user exists in DB
    user = await db.users.find_one({"_id": user_obj_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found in database.")

    return {
        "email": user["email"],
        "authenticated": True
    }

@router.get("/auth/logout")
def logout(response: Response):
    try:
        # Delete the token cookie (clears session)
        response.delete_cookie(
            key="token",
            httponly=True,
            secure=False,
            samesite="none"
        )
        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")

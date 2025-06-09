from fastapi import APIRouter, Request, Response, HTTPException, Depends
from app.controllers import auth_controller
from app.models.user import SignUpRequest, LoginRequest
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

    await auth_controller.create_user(name, email, password, db)
    return {"message": "User created successfully"}

@router.post("/auth/login")
async def login(request: Request, response: Response, data: LoginRequest):
    db = request.app.mongodb
    email = data.email
    password = data.password

    user = await auth_controller.get_user_by_email(email, db)
    if not user or not auth_controller.verify_password(password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth_controller.create_access_token({"sub": str(user["_id"])})

    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        max_age=3600,
        secure=True,
        samesite="none"
    )

    return {"message": "Login successful"}

@router.get("/auth/verify")
async def me(request: Request):
    token = request.cookies.get("token")
    db = request.app.mongodb

    if not token:
        raise HTTPException(status_code=401, detail="Not logged in")

    user_id = auth_controller.decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return {"userId": str(user["_id"]), "email": user["email"], "name": user["name"], "authenticated":True}

@router.get("/auth/logout")
def logout(response: Response):
    response.delete_cookie("token")
    return {"message": "Logged out successfully"}


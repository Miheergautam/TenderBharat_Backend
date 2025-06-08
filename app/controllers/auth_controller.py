from fastapi import HTTPException
from passlib.context import CryptContext
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from jose import jwt, JWTError

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

async def get_user_by_email(email: str, db):
    return await db.users.find_one({"email": email})

async def get_user_by_id(user_id: str, db):
    return await db.users.find_one({"_id": ObjectId(user_id)})

async def create_user(name: str, email: str, password: str, db):
    if await db.users.find_one({"email": email}):
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed = hash_password(password)
    await db.users.insert_one({
        "name": name,
        "email": email,
        "hashed_password": hashed,
    })

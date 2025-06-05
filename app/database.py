import os
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
DATABASE_NAME = os.getenv("DATABASE_NAME", "TenderBharat")

async def startup_db_client(app: FastAPI):
    app.mongodb_client = AsyncIOMotorClient(MONGO_CONNECTION_STRING)
    app.mongodb = app.mongodb_client.get_database(DATABASE_NAME)
    print("MongoDB connected.")

async def shutdown_db_client(app: FastAPI):
    app.mongodb_client.close()
    print("MongoDB disconnected.")

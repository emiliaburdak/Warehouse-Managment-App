import os

from dotenv import load_dotenv
from fastapi import FastAPI
from pymongo import MongoClient

from app.routes import router

load_dotenv()

app = FastAPI()


@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(os.getenv("DB_URI"))
    app.database = app.mongodb_client[os.getenv("DB_NAME")]


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


app.include_router(router)

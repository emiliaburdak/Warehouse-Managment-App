import os

from dotenv import load_dotenv
from fastapi import FastAPI
from pymongo import MongoClient

from app.routes.category_route import router as category_route
from app.routes.part_route import router as part_route
from app.utils.exemplary_data_generator import init_db_with_exemplary_data_if_not_exists

load_dotenv()

app = FastAPI()


# TODO: on_event can be replaced with newer approach i.e. lifespan
# https://fastapi.tiangolo.com/advanced/events/#lifespan
@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(os.getenv("DB_URI"))
    app.database = app.mongodb_client[os.getenv("DB_NAME")]
    init_db_with_exemplary_data_if_not_exists(app.database)

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


app.include_router(part_route)
app.include_router(category_route)

from fastapi import HTTPException, APIRouter, Request

from app.models.category import Category
from app.models.part import Part

router = APIRouter()


@router.get("/")
def home():
    return {"message": "Hello World"}


@router.post("/parts/")
def add_part(request: Request, part: Part):
    db = request.app.database
    existing_part = db.parts.find_one({'serial_number': part.serial_number})
    if existing_part:
        raise HTTPException(status_code=409, detail="Part with this serial number already exists")

    db.parts.insert_one(part.model_dump())
    return part


@router.post("/categories/")
def add_category(request: Request, category: Category):
    db = request.app.database
    existing_category_with_same_name = db.categorys.find_one({'name': category.name})
    parent_category = db.categorys.find_one({'name': category.parent_name})

    if existing_category_with_same_name:
        raise HTTPException(status_code=409, detail="Category with this name number already exists")

    if category.parent_name != '' and parent_category is None:
        raise HTTPException(status_code=400, detail="Category with this parent name does not exist")

    db.categorys.insert_one(category.model_dump())
    return category

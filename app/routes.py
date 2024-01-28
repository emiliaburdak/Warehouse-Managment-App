from fastapi import HTTPException, APIRouter, Request

from app.models.category import Category
from app.models.part import Part

router = APIRouter()


@router.get("/")
def home():
    return {"message": "Hello World"}


@router.post("/parts/")
def add_part(request: Request, part_dto: Part):
    db = request.app.database

    existing_part = db.parts.find_one({'serial_number': part_dto.serial_number})
    if existing_part:
        raise HTTPException(status_code=409, detail="Part with this serial number already exists")

    category = db.categories.find_one({'name': part_dto.category})
    if category is None or category['parent_name'] == '':
        raise HTTPException(status_code=400, detail="Incorrect category, part can't be created")

    db.parts.insert_one(part_dto.model_dump())
    return part_dto


@router.post("/categories/")
def add_category(request: Request, category_dto: Category):
    db = request.app.database

    existing_category_with_same_name = db.categories.find_one({'name': category_dto.name})
    if existing_category_with_same_name:
        raise HTTPException(status_code=409, detail="Category with this name number already exists")

    parent_category = db.categories.find_one({'name': category_dto.parent_name})
    if category_dto.parent_name != '' and parent_category is None:
        raise HTTPException(status_code=400, detail="Category with this parent name does not exist")

    db.categories.insert_one(category_dto.model_dump())
    return category_dto

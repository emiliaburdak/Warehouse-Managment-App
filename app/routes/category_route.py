from fastapi import HTTPException, APIRouter, Request

from app.models.category import Category

router = APIRouter()


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

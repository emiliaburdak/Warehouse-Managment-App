from fastapi import HTTPException, APIRouter, Request
from fastapi.encoders import jsonable_encoder
from app.models.category import Category, UpdateCategory
from app.models.part import Part

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


@router.put("/categories/{category}")
def update_category(category: str, request: Request, update_category_dto: UpdateCategory):
    db = request.app.database

    existing_category = db.categories.find_one({'name': category})
    if not existing_category:
        raise HTTPException(status_code=404, detail="Category not found")

    fields_to_update = {field: value for field, value in update_category_dto.model_dump(exclude_unset=True).items() if
                        value is not None}

    # if there is category to update, change all parent categories in child_categories
    if 'name' in fields_to_update:
        child_categories = db.categories.find({'parent_name': category})
        for child_category in child_categories:
            db.categories.update_one({'name': child_category['name']}, {'$set': {'parent_name': fields_to_update['name']}})
        db.categories.update_one({'name': category}, {'$set': {'name': fields_to_update['name']}})

    if 'parent_name' in fields_to_update:
        if fields_to_update['parent_name'] != '':
            db.categories.update_one({'name': category}, {'$set': {'parent_name': fields_to_update['parent_name']}})
        else:
            # check if there are parts with this category because if true then this category can not be base category
            parts_with_this_category = db.parts.find_one({'category': category})
            if parts_with_this_category:
                raise HTTPException(status_code=400,
                                    detail="This category cannot be a base category because it has associated parts.")
            else:
                db.categories.update_one({'name': category}, {'$set': {'parent_name': ''}})
    updated_category = db.categories.find_one({'name': fields_to_update['name']})
    return jsonable_encoder(updated_category, exclude=['_id'])








from fastapi import HTTPException, APIRouter, Request
from fastapi.encoders import jsonable_encoder
from app.models.category import Category, UpdateCategory
from app.models.part import Part

router = APIRouter()


@router.post("/categories/", status_code=201)
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
            db.categories.update_one({'name': child_category['name']},
                                     {'$set': {'parent_name': fields_to_update['name']}})
        db.categories.update_one({'name': category}, {'$set': {'name': fields_to_update['name']}})

    if 'parent_name' in fields_to_update:
        if fields_to_update['parent_name'] != '':
            db.categories.update_one({'name': category}, {'$set': {'parent_name': fields_to_update['parent_name']}})
        else:
            # check if there are parts with this category because if true then this category can not be base category
            parts_belongs_category = db.parts.find_one({'category': category})
            if parts_belongs_category:
                raise HTTPException(status_code=400,
                                    detail="This category cannot be a base category because it has associated parts.")
            db.categories.update_one({'name': category}, {'$set': {'parent_name': ''}})
    updated_category = db.categories.find_one({'name': fields_to_update['name']})
    return jsonable_encoder(updated_category, exclude=['_id'])


@router.get("/categories/{category}")
def get_category(category: str, request: Request):
    db = request.app.database
    found_category = db.categories.find_one({'name': category})
    if not found_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return jsonable_encoder(found_category, exclude=['_id'])


@router.get("/categories/")
def get_all_categories(request: Request):
    db = request.app.database
    found_categories = db.categories.find({})
    category_list = [Category(**category) for category in found_categories]
    return jsonable_encoder(category_list, exclude=['_id'])


@router.delete("/categories/{category}", status_code=204)
def delete_category(category: str, request: Request):
    db = request.app.database
    # check if category has parts if true -> error
    parts_belongs_category = db.parts.find_one({'category': category})
    if parts_belongs_category:
        raise HTTPException(status_code=400,
                            detail="You can not delete this category because, "
                                   "there are parts that belong to this category.")

    # check if child category has parts if true -> error
    child_categories = list(db.categories.find({'parent_name': category}))
    for child_category in child_categories:
        if db.parts.find_one({'category': child_category['name']}):
            raise HTTPException(status_code=400,
                                detail="You can not delete this category because, "
                                       "there are parts that belong to child category " + child_category['name'])

    # extract parent_name to use it while assigning child_category
    category_to_delete = db.categories.find_one({'name': category})
    category_to_delete_parent_name = category_to_delete['parent_name']

    # delete category
    delete_result = db.categories.delete_one({'name': category})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Part not found")

    # assign child_category['parent_name'] to new parent_name (if it was base category assign to "" so it will be new base category)
    if category_to_delete_parent_name != "":
        for child_category in child_categories:
            db.categories.update_one({'name': child_category['name']},
                                     {'$set': {'parent_name': category_to_delete_parent_name}})
    else:
        for child_category in child_categories:
            db.categories.update_one({'name': child_category['name']},
                                     {'$set': {'parent_name': ""}})



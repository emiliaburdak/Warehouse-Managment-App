from fastapi import HTTPException, APIRouter, Request
from fastapi.encoders import jsonable_encoder
from app.models.category import Category, UpdateCategory

router = APIRouter()


def ensure_that_parent_category_exist(db, parent_name):
    parent_category = db.categories.find_one({'name': parent_name})
    if parent_name != '' and parent_category is None:
        raise HTTPException(status_code=400, detail="Category with this parent name does not exist")


def ensure_that_category_does_not_exist(db, category_name):
    existing_category_with_same_name = db.categories.find_one({'name': category_name})
    if existing_category_with_same_name:
        raise HTTPException(status_code=409, detail="Category with this name already exists")


def ensure_category_not_base_if_parts_exist(db, category):
    parts_belongs_category = db.parts.find_one({'category': category})
    if parts_belongs_category:
        raise HTTPException(status_code=400,
                            detail="This category cannot be a base category because it has associated parts.")


def update_child_categories_parent_name(db, category, fields_to_update):
    child_categories = db.categories.find({'parent_name': category})
    for child_category in child_categories:
        db.categories.update_one({'name': child_category['name']},
                                 {'$set': {'parent_name': fields_to_update['name']}})


def ensure_that_category_exist(db, category):
    existing_category = db.categories.find_one({'name': category})
    if not existing_category:
        raise HTTPException(status_code=404, detail="Category not found")


def update_child_category_parent_name(db, category_to_delete_parent_name, child_categories):
    for child_category in child_categories:
        db.categories.update_one({'name': child_category['name']},
                                 {'$set': {'parent_name': category_to_delete_parent_name}})


def extract_parent_name(db, category):
    category_to_delete = db.categories.find_one({'name': category})
    category_to_delete_parent_name = category_to_delete['parent_name']
    return category_to_delete_parent_name


def prevent_category_delete_if_part_associated_child_category(db, child_categories):
    for child_category in child_categories:
        if db.parts.find_one({'category': child_category['name']}):
            raise HTTPException(status_code=400,
                                detail="You can not delete this category because, "
                                       "there are parts that belong to child category " + child_category['name'])


def prevent_category_delete_if_part_associated(db, category):
    parts_belongs_category = db.parts.find_one({'category': category})
    if parts_belongs_category:
        raise HTTPException(status_code=400,
                            detail="You can not delete this category because, "
                                   "there are parts that belong to this category.")


@router.post("/categories/", status_code=201)
def add_category(request: Request, category_dto: Category):
    db = request.app.database

    ensure_that_category_does_not_exist(db, category_dto.name)

    ensure_that_parent_category_exist(db, category_dto.parent_name)

    db.categories.insert_one(category_dto.model_dump())
    return category_dto


@router.put("/categories/{category}")
def update_category(category: str, request: Request, update_category_dto: UpdateCategory):
    db = request.app.database

    ensure_that_category_exist(db, category)

    fields_to_update = {field: value for field, value in update_category_dto.model_dump(exclude_unset=True).items() if
                        value is not None}

    # if there is category to update, update all parent_name in child_categories and update category
    if 'name' in fields_to_update:
        update_child_categories_parent_name(db, category, fields_to_update)
        db.categories.update_one({'name': category}, {'$set': {'name': fields_to_update['name']}})

    if 'parent_name' in fields_to_update:
        # if category is not base category
        if fields_to_update['parent_name'] != '':
            db.categories.update_one({'name': category}, {'$set': {'parent_name': fields_to_update['parent_name']}})
        else:
            # check if there are parts with this category because if true then this category can not be base category
            ensure_category_not_base_if_parts_exist(db, category)
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
    prevent_category_delete_if_part_associated(db, category)

    # check if child category has parts if true -> error
    child_categories = list(db.categories.find({'parent_name': category}))
    prevent_category_delete_if_part_associated_child_category(db, child_categories)

    # extract parent_name to use it while assigning child_category
    category_to_delete_parent_name = extract_parent_name(db, category)

    # delete category
    delete_result = db.categories.delete_one({'name': category})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Part not found")

    # assign child_category['parent_name'] to new parent_name
    if category_to_delete_parent_name != "":
        update_child_category_parent_name(db, category_to_delete_parent_name, child_categories)
    else:
        update_child_category_parent_name(db, "", child_categories)

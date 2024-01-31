from fastapi import HTTPException


def ensure_that_parent_category_exist(db, parent_name: str):
    parent_category = db.categories.find_one({'name': parent_name})
    if parent_name != '' and parent_category is None:
        raise HTTPException(status_code=400, detail="Category with this parent name does not exist")


def ensure_that_category_does_not_exist(db, category_name: str):
    existing_category_with_same_name = db.categories.find_one({'name': category_name})
    if existing_category_with_same_name:
        raise HTTPException(status_code=409, detail="Category with this name already exists")


def ensure_category_not_base_if_parts_exist(db, category: str):
    parts_belongs_category = db.parts.find_one({'category': category})
    if parts_belongs_category:
        raise HTTPException(status_code=400,
                            detail="This category cannot be a base category because it has associated parts.")


def update_child_categories_parent_name(db, category: str, fields_to_update: dict):
    child_categories = db.categories.find({'parent_name': category})
    for child_category in child_categories:
        db.categories.update_one({'name': child_category['name']},
                                 {'$set': {'parent_name': fields_to_update['name']}})


def ensure_that_category_exist(db, category: str):
    existing_category = db.categories.find_one({'name': category})
    if not existing_category:
        raise HTTPException(status_code=404, detail="Category not found")


def update_child_category_parent_name(db, category_to_delete_parent_name: str, child_categories: list):
    for child_category in child_categories:
        db.categories.update_one({'name': child_category['name']},
                                 {'$set': {'parent_name': category_to_delete_parent_name}})


def extract_parent_name(db, category: str) -> str:
    category_to_delete = db.categories.find_one({'name': category})
    category_to_delete_parent_name = category_to_delete['parent_name']
    return category_to_delete_parent_name


def prevent_category_delete_if_part_associated_child_category(db, child_categories: list):
    for child_category in child_categories:
        if db.parts.find_one({'category': child_category['name']}):
            raise HTTPException(status_code=400,
                                detail="You can not delete this category because, "
                                       "there are parts that belong to child category " + child_category['name'])


def prevent_category_delete_if_part_associated(db, category: str):
    parts_belongs_category = db.parts.find_one({'category': category})
    if parts_belongs_category:
        raise HTTPException(status_code=400,
                            detail="You can not delete this category because, "
                                   "there are parts that belong to this category.")

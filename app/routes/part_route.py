from fastapi import HTTPException, APIRouter, Request, Depends
from fastapi.encoders import jsonable_encoder

from app.models.part import Part, UpdatePart

router = APIRouter()


@router.post("/parts/", status_code=201)
def add_part(request: Request, part_dto: Part):
    db = request.app.database

    existing_part = db.parts.find_one({'serial_number': part_dto.serial_number})
    if existing_part:
        raise HTTPException(status_code=409, detail="Part with this serial number already exists")

    handle_no_parent_category(db, part_dto)

    db.parts.insert_one(part_dto.model_dump())
    return part_dto


def handle_no_parent_category(db, part_dto):
    category = db.categories.find_one({'name': part_dto.category})
    if category is None or category['parent_name'] == '':
        raise HTTPException(status_code=400, detail="Incorrect category, part can't be created")


@router.put("/parts/{serial_number}")
def update_part(serial_number: str, request: Request, update_part_dto: UpdatePart):
    db = request.app.database

    existing_part = db.parts.find_one({'serial_number': serial_number})
    if not existing_part:
        raise HTTPException(status_code=404, detail="Part not found")

    fields_to_update = {field: value for field, value in update_part_dto.model_dump(exclude_unset=True).items() if
                        value is not None}

    if 'category' in fields_to_update:
        handle_no_parent_category(db, update_part_dto)

    db.parts.update_one({'serial_number': serial_number}, {'$set': fields_to_update})
    updated_part = db.parts.find_one({'serial_number': serial_number})
    return jsonable_encoder(updated_part, exclude=['_id'])


@router.get("/parts/{serial_number}")
def get_part(serial_number: str, request: Request):
    db = request.app.database
    found_part = db.parts.find_one({'serial_number': serial_number})
    return jsonable_encoder(found_part, exclude=['_id'])


@router.get("/parts/")
def get_parts(request: Request):
    db = request.app.database
    found_parts = db.parts.find({})
    parts_list = [Part(**part) for part in found_parts]
    return jsonable_encoder(parts_list, exclude=['_id'])


@router.delete("/parts/{serial_number}", status_code=204)
def delete_part(serial_number: str, request: Request):
    db = request.app.database
    delete_result = db.parts.delete_one({'serial_number': serial_number})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Part not found")


@router.get("/parts/search/")
def search_part(request: Request, searched_parameters: UpdatePart = Depends()):
    db = request.app.database
    query = {}

    if searched_parameters.name is not None:
        query['name'] = searched_parameters.name
    if searched_parameters.description is not None:
        query['description'] = searched_parameters.description
    if searched_parameters.category is not None:
        query['category'] = searched_parameters.category
    if searched_parameters.quantity is not None:
        query['quantity'] = searched_parameters.quantity
    if searched_parameters.price is not None:
        query['price'] = searched_parameters.price
    if searched_parameters.location is not None:
        query['location'] = searched_parameters.location.model_dump()

    searched_parts = db.parts.find(query)
    return [Part(**part) for part in searched_parts]






from fastapi import HTTPException, APIRouter, Request
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

    # TODO: handle changing category
    if 'category' in fields_to_update:
        handle_no_parent_category(db, update_part_dto)

    db.parts.update_one({'serial_number': serial_number}, {'$set': fields_to_update})
    updated_part = db.parts.find_one({'serial_number': serial_number})
    return jsonable_encoder(updated_part, exclude=['_id'])





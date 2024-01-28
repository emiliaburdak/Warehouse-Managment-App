from fastapi import HTTPException, APIRouter, Request

from app.models.part import Part

router = APIRouter()


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

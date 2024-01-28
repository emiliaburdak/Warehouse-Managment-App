from fastapi import HTTPException, APIRouter, Request

from app.models import Part

router = APIRouter()


@router.get("/")
def home():
    return {"message": "Hello World"}


@router.post("/parts/")
def add_part(request: Request, part: Part):
    db = request.app.database
    part.serial_number = str(part.serial_number)
    existing_part = db.parts.find_one({'serial_number': part.serial_number})
    if existing_part:
        raise HTTPException(status_code=409, detail="Part with this serial number already exists")

    db.parts.insert_one(part.model_dump())
    return part

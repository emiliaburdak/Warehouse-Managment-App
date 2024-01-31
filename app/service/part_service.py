from fastapi import HTTPException

from app.models.part import Part


def ensure_that_part_does_not_exist(db, serial_number: str):
    existing_part = db.parts.find_one({'serial_number': serial_number})
    if existing_part:
        raise HTTPException(status_code=409, detail="Part with this serial number already exists")


def handle_no_parent_category(db, category: str):
    category = db.categories.find_one({'name': category})
    if category is None or category['parent_name'] == '':
        raise HTTPException(status_code=400, detail="Incorrect category, part can't be created")


def find_part_or_throw_not_found(db, serial_number: str) -> Part:
    existing_part = db.parts.find_one({'serial_number': serial_number})
    if not existing_part:
        raise HTTPException(status_code=404, detail="Part not found")
    return existing_part

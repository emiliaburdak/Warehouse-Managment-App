def generate_part_data(serial_number: str, category: str):
    return {
        "serial_number": serial_number,
        "name": "test_name",
        "description": "test_description",
        "category": category,
        "quantity": 10,
        "price": 19.99,
        "location": {
            "room": "test_room",
            "bookcase": "test_bookcase",
            "shelf": "test_shelf",
            "cuvette": "test_cuvette",
            "column": 7,
            "row": 13}}


def init_db_with_exemplary_data_if_not_exists(db):
    demo_config = list(db.demo_config.find())
    if len(demo_config) > 0 and demo_config[0]['has_inserted_demo_examples']:
        return

    db.categories.insert_one({'name': 'DemoMainCategory', 'parent_name': ''})
    db.categories.insert_one({'name': 'DemoSubCategoryA', 'parent_name': 'DemoMainCategory'})
    db.categories.insert_one({'name': 'DemoSubCategoryB', 'parent_name': 'DemoMainCategory'})

    db.parts.insert_one(generate_part_data('sn1', 'DemoSubCategoryA'))
    db.parts.insert_one(generate_part_data('sn2', 'DemoSubCategoryA'))
    db.parts.insert_one(generate_part_data('sn3', 'DemoSubCategoryA'))

    db.parts.insert_one(generate_part_data('sn4', 'DemoSubCategoryB'))
    db.parts.insert_one(generate_part_data('sn5', 'DemoSubCategoryB'))
    db.parts.insert_one(generate_part_data('sn6', 'DemoSubCategoryB'))

    db.demo_config.insert_one({'has_inserted_demo_examples': True})

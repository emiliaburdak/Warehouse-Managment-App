import os
from http import HTTPStatus
from unittest import TestCase

from fastapi.testclient import TestClient
from pymongo import MongoClient

from app.main import app

client = TestClient(app)


class TestCategoryRoute(TestCase):
    @classmethod
    def setUpClass(cls):
        app.mongodb_client = MongoClient(os.getenv("TEST_DB_URI"))
        app.database = app.mongodb_client[os.getenv("TEST_DB_NAME")]

    @classmethod
    def setUp(cls):
        app.mongodb_client.drop_database(os.getenv("TEST_DB_NAME"))

    @classmethod
    def tearDownClass(cls):
        app.mongodb_client.drop_database(os.getenv("TEST_DB_NAME"))
        app.mongodb_client.close()

    def test_add_categories(self):
        response = client.post("/categories/", json={
            'name': 'category_A',
            'parent_name': ''
        })
        assert response.status_code == HTTPStatus.CREATED

        second_response = client.post("/categories/", json={
            'name': 'subcategory_A1',
            'parent_name': 'category_A'
        })
        assert second_response.status_code == HTTPStatus.CREATED

    def test_require_valid_parent_category(self):
        response = client.post("/categories/", json={
            'name': 'category_A',
            'parent_name': 'category_Z'
        })
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_update_category(self):
        client.post("/categories/", json={
            'name': 'category_A',
            'parent_name': ''
        })
        client.post("/categories/", json={
            'name': 'subcategory_A1',
            'parent_name': 'category_A'
        })
        client.post("/categories/", json={
            'name': 'subcategory_A2',
            'parent_name': 'category_A'
        })

        response = client.put("/categories/category_A", json={
            'name': 'category_B',
            'parent_name': ''
        })

        assert response.status_code == HTTPStatus.OK
        assert response.json()['name'] == 'category_B'
        # TODO: add test to check if the child parent_name has been changed

    def test_update_parent_name(self):
        client.post("/categories/", json={
            'name': 'category_A',
            'parent_name': ''
        })
        client.post("/categories/", json={
            'name': 'category_B',
            'parent_name': ''
        })
        client.post("/categories/", json={
            'name': 'subcategory',
            'parent_name': 'category_A'
        })

        response = client.put("/categories/subcategory", json={
            'name': 'subcategory',
            'parent_name': 'category_B'
        })

        assert response.status_code == HTTPStatus.OK
        assert response.json()['parent_name'] == 'category_B'

    @staticmethod
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
                "column": "test_column",

                "row": "test_row"}}

    def test_reject_base_category_update_for_category_containing_parts(self):
        client.post("/categories/", json={
            'name': 'category_A',
            'parent_name': ''
        })

        client.post("/categories/", json={
            'name': 'subcategory',
            'parent_name': 'category_A'
        })

        part_data = self.generate_part_data(serial_number='111', category='subcategory')
        client.post("/parts/", json=part_data)

        response = client.put("/categories/subcategory", json={
            'name': 'subcategory',
            'parent_name': ''
        })
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_update_category_to_base_category_if_no_parts(self):
        client.post("/categories/", json={
            'name': 'category_A',
            'parent_name': ''
        })

        client.post("/categories/", json={
            'name': 'subcategory',
            'parent_name': 'category_A'
        })

        part_data = self.generate_part_data(serial_number='111', category='not_matching_category')
        client.post("/parts/", json=part_data)

        response = client.put("/categories/subcategory", json={
            'name': 'subcategory',
            'parent_name': ''
        })
        assert response.status_code == HTTPStatus.OK
        assert response.json()['name'] == 'subcategory'
        assert response.json()['parent_name'] == ''

    def test_get_category(self):
        client.post("/categories/", json={
            'name': 'category_A',
            'parent_name': ''
        })

        client.post("/categories/", json={
            'name': 'subcategory',
            'parent_name': 'category_A'
        })

        response = client.get("/categories/subcategory")
        assert response.status_code == HTTPStatus.OK
        assert response.json()['name'] == "subcategory"
        assert response.json()['parent_name'] == "category_A"

    def test_get_all_categories(self):
        client.post("/categories/", json={
            'name': 'category_A',
            'parent_name': ''
        })

        client.post("/categories/", json={
            'name': 'subcategory',
            'parent_name': 'category_A'
        })

        client.post("/categories/", json={
            'name': 'sub_subcategory',
            'parent_name': 'subcategory'
        })

        response = client.get("/categories/")
        assert response.status_code == HTTPStatus.OK

        response_data = response.json()
        categories_names_list = [category['name'] for category in response_data]
        assert 'subcategory' in categories_names_list
        assert 'sub_subcategory' in categories_names_list
        assert 'category_A' in categories_names_list

    def test_prevent_delete_category_if_category_contain_parts(self):
        client.post("/categories/", json={
            'name': 'category_A',
            'parent_name': ''
        })

        client.post("/categories/", json={
            'name': 'subcategory_A',
            'parent_name': 'category_A'
        })

        client.post("/categories/", json={
            'name': 'sub_subcategory_A',
            'parent_name': 'subcategory_A'
        })

        part_data = self.generate_part_data(serial_number='111', category='subcategory_A')
        client.post("/parts/", json=part_data)

        result = client.delete("/categories/subcategory_A")
        assert result.status_code == HTTPStatus.BAD_REQUEST

    def test_prevent_delete_category_if_child_category_contain_parts(self):
        client.post("/categories/", json={
            'name': 'category_A',
            'parent_name': ''
        })

        client.post("/categories/", json={
            'name': 'subcategory_A',
            'parent_name': 'category_A'
        })

        client.post("/categories/", json={
            'name': 'sub_subcategory_A',
            'parent_name': 'subcategory_A'
        })

        part_data = self.generate_part_data(serial_number='111', category='sub_subcategory_A')
        client.post("/parts/", json=part_data)

        result = client.delete("/categories/subcategory_A")
        assert result.status_code == HTTPStatus.BAD_REQUEST

    def test_delete_category(self):
        # if there are no parts in category and child category
        # we are deleting category and update child category 'parent_name'

        client.post("/categories/", json={
            'name': 'category_A',
            'parent_name': ''
        })

        client.post("/categories/", json={
            'name': 'subcategory_A',
            'parent_name': 'category_A'
        })

        client.post("/categories/", json={
            'name': 'sub_subcategory_A',
            'parent_name': 'subcategory_A'
        })

        result = client.delete("/categories/subcategory_A")
        assert result.status_code == HTTPStatus.NO_CONTENT
        response = client.get("/categories/sub_subcategory_A")
        assert response.json()['parent_name'] == 'category_A'

    def test_delete_base_category(self):
        # if parent_category was base category now child category become base category

        client.post("/categories/", json={
            'name': 'category_A',
            'parent_name': ''
        })

        client.post("/categories/", json={
            'name': 'subcategory_A',
            'parent_name': 'category_A'
        })

        client.post("/categories/", json={
            'name': 'sub_subcategory_A',
            'parent_name': 'subcategory_A'
        })

        result = client.delete("/categories/category_A")
        assert result.status_code == HTTPStatus.NO_CONTENT
        response = client.get("/categories/subcategory_A")
        assert response.json()['parent_name'] == ''

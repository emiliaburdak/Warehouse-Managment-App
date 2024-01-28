import os
from http import HTTPStatus
from unittest import TestCase

from fastapi.testclient import TestClient
from pymongo import MongoClient

from app.main import app

client = TestClient(app)


class TestRoutes(TestCase):
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

    def test_read_main(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello World"}

    def test_add_part_with_unique_serial_number(self):
        part_data = {
            "serial_number": "123",
            "name": "test_name",
            "description": "test_description",
            "category": "test_category",
            "quantity": 10,
            "price": 19.99,
            "location": {
                "room": "test_room",
                "bookcase": "test_bookcase",
                "shelf": "test_shelf",
                "cuvette": "test_cuvette",
                "column": "test_column",
                "row": "test_row"}}

        response = client.post("/parts/", json=part_data)
        assert response.status_code == HTTPStatus.OK

        # ensure it's not possible to add part with the same serial_number
        second_response = client.post("/parts/", json=part_data)
        assert second_response.status_code == HTTPStatus.CONFLICT

    def test_add_categories(self):
        response = client.post("/categories/", json={
            'name': 'category_A',
            'parent_name': ''
        })
        assert response.status_code == HTTPStatus.OK

        second_response = client.post("/categories/", json={
            'name': 'subcategory_A1',
            'parent_name': 'category_A'
        })
        assert second_response.status_code == HTTPStatus.OK

    def test_require_valid_parent_category(self):
        response = client.post("/categories/", json={
            'name': 'category_A',
            'parent_name': 'category_Z'
        })
        assert response.status_code == HTTPStatus.BAD_REQUEST

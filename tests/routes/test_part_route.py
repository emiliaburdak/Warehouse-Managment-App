import os
from http import HTTPStatus
from unittest import TestCase

from fastapi.testclient import TestClient
from pymongo import MongoClient

from app.main import app

client = TestClient(app)


class TestPartRoute(TestCase):
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

    def test_add_part_with_unique_serial_number_and_non_base_category(self):
        # create base category category_A
        client.post("/categories/", json={
            'name': 'category_A',
            'parent_name': ''
        })

        # create category subcategory_A
        client.post("/categories/", json={
            'name': 'subcategory_A',
            'parent_name': 'category_A'
        })

        part_data = self.generate_part_data(serial_number='#1', category='subcategory_A')
        response = client.post("/parts/", json=part_data)
        assert response.status_code == HTTPStatus.OK

        # ensure it's not possible to add part with the same serial_number
        second_response = client.post("/parts/", json=part_data)
        assert second_response.status_code == HTTPStatus.CONFLICT

    def test_prevent_adding_part_with_base_category(self):
        # create base category category_A
        client.post("/categories/", json={
            'name': 'category_A',
            'parent_name': ''
        })

        part_data = self.generate_part_data(serial_number='#1', category='category_A')
        response = client.post("/parts/", json=part_data)
        assert response.status_code == HTTPStatus.BAD_REQUEST

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
    def tearDownClass(cls):
        app.mongodb_client.drop_database(os.getenv("TEST_DB_NAME"))
        app.mongodb_client.close()

    def test_read_main(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello World"}

    def test_add_part(self):
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

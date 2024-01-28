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

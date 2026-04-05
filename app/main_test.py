from starlette.testclient import TestClient
from .main import app
import json

client = TestClient(app)

def test_sanity():
	response = client.get("/hello")
	assert response.status_code == 200
	assert response.json() == {"Hello": "World"}
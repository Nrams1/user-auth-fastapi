
import main
from fastapi.testclient import TestClient

# Tests----------------
"""
1. Happy path : user created an account success
2. Sad Path : user already exist
3. Edges : wrong email
"""


client = TestClient(main.app)
def test_sign_up_success():
    response = client.post("/auth/signup/",json={"email":"neo@test.com","password":"neo"})
    assert response.status_code == 201
    assert response.json() == {"email":"neo@test.com"}

def test_sign_up_fail():
    response = client.post("/auth/signup/",json={"email":"neo@test.com","password":"neo"})
    assert response.status_code == 409
    assert response.message == {"detail":"An account with this email address already exists"}

# Spin up a new db everytime you run a test?
# pytest fixtures 

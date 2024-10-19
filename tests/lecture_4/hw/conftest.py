import pytest
from fastapi.testclient import TestClient
from faker import Faker
import base64
from http import HTTPStatus
from pydantic import SecretStr
from lecture_4.demo_service.api.contracts import UserResponse, RegisterUserRequest
from lecture_4.demo_service.api.main import create_app
from lecture_4.demo_service.core.users import UserInfo, UserRole

app = create_app()
faker = Faker()

@pytest.fixture()
def api_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture()
def test_birthdate():
    return faker.date_time().isoformat()

@pytest.fixture()
def test_password():
    return "securepassword123"

@pytest.fixture()
def admin_credentials():
    return base64.b64encode("admin:superSecretAdminPassword123".encode()).decode()

@pytest.fixture()
def admin_auth_header(admin_credentials):
    return {"Authorization": f"Basic {admin_credentials}"}

@pytest.fixture()
def expected_user_info(test_birthdate, test_password):
    return UserInfo(
        username="testuser",
        name="Test User",
        birthdate=test_birthdate,
        role=UserRole.USER,
        password=SecretStr(test_password)
    )

@pytest.fixture()
def existing_user(api_client, test_password, test_birthdate, expected_user_info):
    user_data = {
        'username': expected_user_info.username,
        'name': expected_user_info.name,
        'birthdate': test_birthdate,
        'password': test_password,
    }
    response = api_client.post('/user-register', json=user_data)
    assert response.status_code == HTTPStatus.OK
    result = response.json()
    return UserResponse(
        uid=result['uid'],
        username=user_data['username'],
        name=user_data['name'],
        birthdate=user_data['birthdate'],
        role=result['role']
    )

@pytest.fixture()
def registration_data(expected_user_info, test_password):
    return RegisterUserRequest(
        username=expected_user_info.username,
        name=expected_user_info.name,
        birthdate=expected_user_info.birthdate,
        password=test_password
    )

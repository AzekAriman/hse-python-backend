import pytest
import base64
from http import HTTPStatus
from faker import Faker

faker = Faker()

class TestUserRegistration:
    def test_user_registration(self, api_client, registration_data, expected_user_info, test_birthdate, test_password):
        print(registration_data)
        response = api_client.post('/user-register', json={
            'username': registration_data.username,
            'name': registration_data.name,
            'birthdate': test_birthdate,
            'password': test_password,
        })
        result = response.json()
        assert response.status_code == HTTPStatus.OK
        assert result['username'] == expected_user_info.username
        assert result['name'] == expected_user_info.name
        assert result['birthdate'] == test_birthdate

    def test_existing_user_registration(self, api_client, existing_user, test_password, test_birthdate):
        response = api_client.post('/user-register', json={
            'username': existing_user.username,
            'name': existing_user.name,
            'birthdate': test_birthdate,
            'password': test_password,
        })
        assert response.status_code == HTTPStatus.BAD_REQUEST

    @pytest.mark.parametrize("invalid_pass", ["short123", "passwordwithoutnumber"])
    def test_registration_with_invalid_password(self, api_client, invalid_pass):
        response = api_client.post('/user-register', json={
            'username': 'sampleuser',
            'name': 'Sample User',
            'birthdate': faker.date_time().isoformat(),
            'password': invalid_pass,
        })
        assert response.status_code == HTTPStatus.BAD_REQUEST

class TestUserRetrieval:
    def test_retrieve_user(self, api_client, existing_user, admin_auth_header):
        response = api_client.post(
            "/user-get",
            params={'id': existing_user.uid},
            headers=admin_auth_header,
        )
        result = response.json()
        assert response.status_code == HTTPStatus.OK
        assert result['username'] == existing_user.username
        assert result['uid'] == existing_user.uid
        assert result['role'] == existing_user.role

    @pytest.mark.parametrize("nonexistent_username, expected_status", [
        ('unknown_user', HTTPStatus.NOT_FOUND),
        ('', HTTPStatus.NOT_FOUND),
    ])
    def test_retrieve_nonexistent_user(self, api_client, admin_auth_header, nonexistent_username, expected_status):
        response = api_client.post(
            "/user-get",
            params={'username': nonexistent_username},
            headers=admin_auth_header,
        )
        assert response.status_code == expected_status

    @pytest.mark.parametrize("credentials, expected_status", [
        (base64.b64encode("admin:wrongpassword".encode()).decode(), HTTPStatus.UNAUTHORIZED),
        (base64.b64encode("invalid_user:correctpassword123".encode()).decode(), HTTPStatus.UNAUTHORIZED),
    ])
    def test_retrieve_user_with_invalid_credentials(self, api_client, existing_user, credentials, expected_status):
        response = api_client.post(
            "/user-get",
            params={'id': existing_user.uid},
            headers={"Authorization": f"Basic {credentials}"},
        )
        assert response.status_code == expected_status

class TestUserPromotion:
    def test_promote_user(self, api_client, existing_user, admin_auth_header):
        response = api_client.post(
            '/user-promote',
            params={'id': existing_user.uid},
            headers=admin_auth_header
        )
        assert response.status_code == HTTPStatus.OK

    def test_promote_user_without_permission(self, api_client, existing_user, test_password):
        user_credentials = base64.b64encode(f"{existing_user.username}:{test_password}".encode()).decode()
        response = api_client.post(
            '/user-promote',
            params={'id': existing_user.uid},
            headers={"Authorization": f"Basic {user_credentials}"}
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_promote_nonexistent_user(self, api_client, admin_auth_header):
        random_id = faker.random_int(1000, 2000)
        response = api_client.post(
            '/user-promote',
            params={'id': random_id},
            headers=admin_auth_header
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST

class TestUserGetRequestValidation:
    def test_provide_both_username_and_id(self, api_client, existing_user, admin_auth_header):
        response = api_client.post(
            "/user-get",
            params={'username': existing_user.username, 'id': existing_user.uid},
            headers=admin_auth_header,
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_provide_neither_username_nor_id(self, api_client, admin_auth_header):
        response = api_client.post(
            "/user-get",
            headers=admin_auth_header,
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST

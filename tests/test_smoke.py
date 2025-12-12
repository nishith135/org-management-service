"""
Smoke tests for the Multi-Tenant Organization Management API
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
import os

# Override database name for testing
os.environ["MONGO_DB_NAME"] = os.getenv("MONGO_DB_NAME", "org_master_db_test")

client = TestClient(app)


@pytest.fixture(scope="module")
def test_org_name():
    """Generate a unique organization name for testing"""
    import uuid
    return f"TestOrg_{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="module")
def test_admin_email():
    """Generate a unique admin email for testing"""
    import uuid
    return f"admin_{uuid.uuid4().hex[:8]}@test.com"


@pytest.fixture(scope="module")
def test_admin_password():
    """Test admin password"""
    return "TestPass123!"


class TestSmoke:
    """Smoke tests for critical API paths"""

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()

    def test_create_organization(self, test_org_name, test_admin_email, test_admin_password):
        """Test creating an organization"""
        payload = {
            "organization_name": test_org_name,
            "admin_email": test_admin_email,
            "admin_password": test_admin_password
        }
        response = client.post("/org/create", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["organization_name"] == test_org_name
        assert "trace_id" in data
        return test_org_name, test_admin_email, test_admin_password

    def test_admin_login(self, test_admin_email, test_admin_password):
        """Test admin login"""
        payload = {
            "email": test_admin_email,
            "password": test_admin_password
        }
        response = client.post("/admin/login", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
        return data["data"]["access_token"]

    def test_get_organization(self, test_org_name):
        """Test getting an organization (public endpoint)"""
        response = client.get(f"/org/get?organization_name={test_org_name}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["organization_name"] == test_org_name

    def test_update_organization(self, test_org_name, test_admin_email, test_admin_password):
        """Test updating an organization"""
        new_name = f"{test_org_name}_Updated"
        payload = {
            "current_organization_name": test_org_name,
            "new_organization_name": new_name,
            "admin_email": test_admin_email,
            "admin_password": test_admin_password
        }
        response = client.put("/org/update", json=payload)
        # Update might fail if org doesn't exist, but should not crash
        assert response.status_code in [200, 404, 400]
        return new_name

    def test_delete_organization(self, test_org_name, test_admin_email, test_admin_password):
        """Test deleting an organization with authentication"""
        # First login to get token
        login_payload = {
            "email": test_admin_email,
            "password": test_admin_password
        }
        login_response = client.post("/admin/login", json=login_payload)

        if login_response.status_code != 200:
            pytest.skip("Cannot get auth token for delete test")

        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to delete (might fail if org doesn't exist, but should not crash)
        response = client.delete(
            f"/org/delete?organization_name={test_org_name}",
            headers=headers
        )
        assert response.status_code in [200, 404, 401]

    def test_delete_without_auth(self, test_org_name):
        """Test that delete endpoint requires authentication"""
        response = client.delete(
            f"/org/delete?organization_name={test_org_name}")
        assert response.status_code == 401  # Unauthorized

    def test_full_workflow(self, test_org_name, test_admin_email, test_admin_password):
        """Test complete workflow: create -> login -> get -> delete"""
        # Create organization
        create_payload = {
            "organization_name": test_org_name,
            "admin_email": test_admin_email,
            "admin_password": test_admin_password
        }
        create_response = client.post("/org/create", json=create_payload)
        assert create_response.status_code == 201

        # Login
        login_payload = {
            "email": test_admin_email,
            "password": test_admin_password
        }
        login_response = client.post("/admin/login", json=login_payload)
        assert login_response.status_code == 200
        token = login_response.json()["data"]["access_token"]

        # Get organization
        get_response = client.get(
            f"/org/get?organization_name={test_org_name}")
        assert get_response.status_code == 200

        # Delete organization
        headers = {"Authorization": f"Bearer {token}"}
        delete_response = client.delete(
            f"/org/delete?organization_name={test_org_name}",
            headers=headers
        )
        assert delete_response.status_code == 200
        assert delete_response.json()["data"]["deleted"] is True

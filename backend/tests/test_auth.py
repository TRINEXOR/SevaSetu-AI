"""
SevaSetu AI — Authentication Tests
Author: Rahul Jha | Made in India 🇮🇳
"""
import pytest
from httpx import AsyncClient
from app.main import app

BASE = "http://test"

@pytest.fixture
def new_user():
    return {
        "name": "Test Citizen",
        "email": "testcitizen@sevasetu.ai",
        "mobile": "9876543210",
        "password": "Test@1234",
        "state": "Maharashtra",
        "language": "en",
    }

@pytest.mark.asyncio
async def test_register_success(new_user):
    async with AsyncClient(app=app, base_url=BASE) as client:
        res = await client.post("/api/v1/auth/register", json=new_user)
    assert res.status_code == 201
    data = res.json()
    assert data["success"] is True
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == new_user["email"]
    assert data["user"]["role"] == "user"

@pytest.mark.asyncio
async def test_register_duplicate_email(new_user):
    async with AsyncClient(app=app, base_url=BASE) as client:
        await client.post("/api/v1/auth/register", json=new_user)
        res = await client.post("/api/v1/auth/register", json=new_user)
    assert res.status_code == 409

@pytest.mark.asyncio
async def test_register_invalid_mobile(new_user):
    new_user["mobile"] = "12345"  # Invalid Indian number
    async with AsyncClient(app=app, base_url=BASE) as client:
        res = await client.post("/api/v1/auth/register", json=new_user)
    assert res.status_code == 422

@pytest.mark.asyncio
async def test_register_weak_password(new_user):
    new_user["password"] = "weak"
    async with AsyncClient(app=app, base_url=BASE) as client:
        res = await client.post("/api/v1/auth/register", json=new_user)
    assert res.status_code == 422

@pytest.mark.asyncio
async def test_login_success(new_user):
    async with AsyncClient(app=app, base_url=BASE) as client:
        await client.post("/api/v1/auth/register", json=new_user)
        res = await client.post(
            "/api/v1/auth/login",
            data={"username": new_user["email"], "password": new_user["password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    assert res.status_code == 200
    assert "access_token" in res.json()

@pytest.mark.asyncio
async def test_login_wrong_password(new_user):
    async with AsyncClient(app=app, base_url=BASE) as client:
        await client.post("/api/v1/auth/register", json=new_user)
        res = await client.post(
            "/api/v1/auth/login",
            data={"username": new_user["email"], "password": "wrongpass"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    assert res.status_code == 401

@pytest.mark.asyncio
async def test_protected_route_no_token():
    async with AsyncClient(app=app, base_url=BASE) as client:
        res = await client.get("/api/v1/auth/me")
    assert res.status_code == 401

@pytest.mark.asyncio
async def test_get_me_with_valid_token(new_user):
    async with AsyncClient(app=app, base_url=BASE) as client:
        reg = await client.post("/api/v1/auth/register", json=new_user)
        token = reg.json()["access_token"]
        res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == new_user["email"]

@pytest.mark.asyncio
async def test_admin_route_as_user(new_user):
    async with AsyncClient(app=app, base_url=BASE) as client:
        reg = await client.post("/api/v1/auth/register", json=new_user)
        token = reg.json()["access_token"]
        res = await client.get("/api/v1/admin/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403

@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(app=app, base_url=BASE) as client:
        res = await client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

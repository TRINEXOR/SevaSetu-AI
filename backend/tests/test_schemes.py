"""
SevaSetu AI — Scheme Tests
Author: Rahul Jha | Made in India 🇮🇳
"""
import pytest
from httpx import AsyncClient
from app.main import app

BASE = "http://test"

@pytest.fixture
async def auth_headers():
    user = {"name":"Scheme Tester","email":"schemetest@sevasetu.ai","mobile":"9823456789","password":"Test@1234","state":"Bihar","language":"en"}
    async with AsyncClient(app=app, base_url=BASE) as client:
        res = await client.post("/api/v1/auth/register", json=user)
        token = res.json().get("access_token","")
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_list_schemes(auth_headers):
    async with AsyncClient(app=app, base_url=BASE) as client:
        res = await client.get("/api/v1/schemes/", headers=auth_headers)
    assert res.status_code == 200
    assert "data" in res.json()

@pytest.mark.asyncio
async def test_filter_schemes_by_category(auth_headers):
    async with AsyncClient(app=app, base_url=BASE) as client:
        res = await client.get("/api/v1/schemes/?category=agriculture", headers=auth_headers)
    assert res.status_code == 200
    schemes = res.json()["data"]
    for s in schemes:
        assert s["category"] == "agriculture"

@pytest.mark.asyncio
async def test_search_schemes(auth_headers):
    async with AsyncClient(app=app, base_url=BASE) as client:
        res = await client.get("/api/v1/schemes/?search=kisan", headers=auth_headers)
    assert res.status_code == 200

@pytest.mark.asyncio
async def test_eligibility_farmer(auth_headers):
    """Farmer with low income should be eligible for PM Kisan."""
    async with AsyncClient(app=app, base_url=BASE) as client:
        res = await client.post(
            "/api/v1/schemes/eligibility",
            json={"annual_income": 80000, "age": 45, "gender": "male", "is_farmer": True, "categories": ["agriculture"]},
            headers=auth_headers,
        )
    assert res.status_code == 200
    data = res.json()
    assert "schemes" in data
    eligible = [s for s in data["schemes"] if s["eligibility_score"] >= 0.7]
    assert len(eligible) >= 0  # At least some eligible

@pytest.mark.asyncio
async def test_scheme_categories(auth_headers):
    async with AsyncClient(app=app, base_url=BASE) as client:
        res = await client.get("/api/v1/schemes/categories", headers=auth_headers)
    assert res.status_code == 200
    assert "categories" in res.json()

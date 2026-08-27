"""
SevaSetu AI — AI Query Tests
Author: Rahul Jha | Made in India 🇮🇳
"""
import pytest
from httpx import AsyncClient
from app.main import app

BASE = "http://test"

@pytest.fixture
async def auth_headers():
    """Register + login, return auth headers."""
    user = {
        "name": "Query Test User",
        "email": "querytest@sevasetu.ai",
        "mobile": "9812345678",
        "password": "Test@1234",
        "state": "Delhi",
        "language": "en",
    }
    async with AsyncClient(app=app, base_url=BASE) as client:
        res = await client.post("/api/v1/auth/register", json=user)
        token = res.json().get("access_token", "")
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_ask_voter_id(auth_headers):
    """Voter ID query should return relevant response."""
    async with AsyncClient(app=app, base_url=BASE) as client:
        res = await client.post(
            "/api/v1/queries/ask",
            json={"question": "How to apply for Voter ID?", "language": "en"},
            headers=auth_headers,
        )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["query_id"] > 0
    assert len(data["answer"]) > 50
    assert data["confidence"] >= 0

@pytest.mark.asyncio
async def test_ask_pan_card(auth_headers):
    """PAN card query should mention key details."""
    async with AsyncClient(app=app, base_url=BASE) as client:
        res = await client.post(
            "/api/v1/queries/ask",
            json={"question": "Documents needed for PAN card?", "language": "en"},
            headers=auth_headers,
        )
    assert res.status_code == 200
    answer = res.json()["answer"].lower()
    # Should mention Aadhaar or Form 49A
    assert any(kw in answer for kw in ["aadhaar", "form", "pan", "document"])

@pytest.mark.asyncio
async def test_ask_empty_question(auth_headers):
    """Empty question should return 400."""
    async with AsyncClient(app=app, base_url=BASE) as client:
        res = await client.post(
            "/api/v1/queries/ask",
            json={"question": "", "language": "en"},
            headers=auth_headers,
        )
    assert res.status_code == 400

@pytest.mark.asyncio
async def test_ask_question_too_long(auth_headers):
    """Question over 1000 chars should return 400."""
    async with AsyncClient(app=app, base_url=BASE) as client:
        res = await client.post(
            "/api/v1/queries/ask",
            json={"question": "x" * 1001, "language": "en"},
            headers=auth_headers,
        )
    assert res.status_code == 400

@pytest.mark.asyncio
async def test_query_saved_to_history(auth_headers):
    """Query should be saved and retrievable from history."""
    async with AsyncClient(app=app, base_url=BASE) as client:
        # Ask a question
        ask = await client.post(
            "/api/v1/queries/ask",
            json={"question": "What is PM Kisan Yojana?", "language": "en"},
            headers=auth_headers,
        )
        assert ask.status_code == 200

        # Check history
        hist = await client.get("/api/v1/queries/history", headers=auth_headers)
        assert hist.status_code == 200
        assert hist.json()["total"] >= 1
        questions = [q["question"] for q in hist.json()["data"]]
        assert "What is PM Kisan Yojana?" in questions

@pytest.mark.asyncio
async def test_get_suggestions(auth_headers):
    """Suggestions endpoint should return list of suggestions."""
    async with AsyncClient(app=app, base_url=BASE) as client:
        res = await client.get(
            "/api/v1/queries/suggestions?language=en",
            headers=auth_headers,
        )
    assert res.status_code == 200
    assert "suggestions" in res.json()
    assert len(res.json()["suggestions"]) > 0

@pytest.mark.asyncio
async def test_delete_query(auth_headers):
    """Should be able to delete own query."""
    async with AsyncClient(app=app, base_url=BASE) as client:
        ask = await client.post(
            "/api/v1/queries/ask",
            json={"question": "Test delete query", "language": "en"},
            headers=auth_headers,
        )
        qid = ask.json()["query_id"]
        del_res = await client.delete(f"/api/v1/queries/{qid}", headers=auth_headers)
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

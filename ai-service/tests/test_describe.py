from unittest.mock import patch

def test_describe_success(client):

    mock_response = """
    {
        "category": "Environmental",
        "severity": "High",
        "summary": "Carbon emissions exceed standards",
        "impact": {
            "financial": "Potential fines",
            "legal": "Regulatory risk",
            "brand": "Reputation damage"
        },
        "explanation": "High emissions increase ESG risk"
    }
    """

    with patch("routes.describe.call_groq", return_value=mock_response):

        response = client.post(
            "/describe",
            json={
                "text": "High carbon emissions"
            }
        )

        data = response.get_json()

        assert response.status_code == 200
        assert "analysis" in data
        assert data["is_fallback"] is False


def test_describe_empty_input(client):

    response = client.post(
        "/describe",
        json={
            "text": ""
        }
    )

    assert response.status_code == 400


def test_describe_invalid_json(client):

    response = client.post(
        "/describe",
        data="plain text",
        content_type="text/plain"
    )

    assert response.status_code == 400
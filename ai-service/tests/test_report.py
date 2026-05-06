from unittest.mock import patch

def test_report_success(client):

    mock_response = """
    {
        "title": "ESG Risk Report",
        "summary": "Summary",
        "overview": "Overview",
        "key_items": ["Risk 1"],
        "recommendations": ["Recommendation 1"]
    }
    """

    with patch("routes.report.call_groq", return_value=mock_response):

        response = client.post(
            "/generate-report",
            json={
                "text": "Carbon emissions"
            }
        )

        data = response.get_json()

        assert response.status_code == 200
        assert "title" in data


def test_report_empty_input(client):

    response = client.post(
        "/generate-report",
        json={
            "text": ""
        }
    )

    assert response.status_code == 400


def test_report_invalid_json(client):

    response = client.post(
        "/generate-report",
        data="plain text",
        content_type="text/plain"
    )

    assert response.status_code == 400
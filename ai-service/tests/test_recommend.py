from unittest.mock import patch

def test_recommend_success(client):

    mock_response = """
    [
        {
            "action_type": "Compliance",
            "description": "Reduce emissions",
            "priority": "High"
        },
        {
            "action_type": "Operational",
            "description": "Improve monitoring",
            "priority": "Medium"
        },
        {
            "action_type": "Strategic",
            "description": "Create ESG policy",
            "priority": "High"
        }
    ]
    """

    with patch("routes.recommend.call_groq", return_value=mock_response):

        response = client.post(
            "/recommend",
            json={
                "text": "Carbon emissions"
            }
        )

        data = response.get_json()

        assert response.status_code == 200
        assert len(data["recommendations"]) == 3


def test_recommend_empty_input(client):

    response = client.post(
        "/recommend",
        json={
            "text": ""
        }
    )

    assert response.status_code == 400


def test_recommend_invalid_json(client):

    response = client.post(
        "/recommend",
        data="plain text",
        content_type="text/plain"
    )

    assert response.status_code == 400
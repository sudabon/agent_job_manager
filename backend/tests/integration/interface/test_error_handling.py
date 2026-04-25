"""Error handling integration tests."""

from __future__ import annotations


def test_unknown_exception_response_hides_internal_details(client) -> None:
    def raise_unknown_error() -> None:
        raise RuntimeError("database password leaked from internal stack")

    client.app.router.add_api_route("/test/unknown-error", raise_unknown_error, methods=["GET"])

    response = client.get("/test/unknown-error", headers={"X-Request-Id": "rid_test"})

    assert response.status_code == 500
    assert response.json() == {
        "detail": "internal server error",
        "request_id": "rid_test",
    }
    assert response.headers["X-Request-Id"] == "rid_test"
    response_body = response.text
    assert "database password leaked" not in response_body
    assert "RuntimeError" not in response_body


def test_invalid_timeout_remains_bad_request(client, api_key) -> None:
    _, plain_key = api_key

    response = client.post(
        "/v1/jobs/python",
        json={"code": "print('hello')", "timeout_sec": 9999},
        headers={"X-API-Key": plain_key},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "timeout_sec must be between 1 and 300"}

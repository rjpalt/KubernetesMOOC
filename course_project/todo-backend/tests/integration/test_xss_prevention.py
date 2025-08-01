"""XSS Prevention Tests for Todo Backend.

Tests to ensure Cross-Site Scripting (XSS) vulnerabilities are properly prevented.
"""

import pytest
from httpx import AsyncClient


class TestXSSPrevention:
    """Test XSS prevention mechanisms."""

    @pytest.mark.asyncio
    async def test_xss_payload_storage_safety(self, test_client: AsyncClient):
        """Test that XSS payloads are stored safely without execution."""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>",
            "<iframe src='javascript:alert(\"xss\")'></iframe>",
            "<object data='javascript:alert(\"xss\")'></object>",
            "<embed src='javascript:alert(\"xss\")'></embed>",
            "<link rel='stylesheet' href='javascript:alert(\"xss\")'>",
            "<style>@import'javascript:alert(\"xss\")';</style>",
            "<input type='image' src='x' onerror='alert(\"xss\")'>",
        ]

        for payload in xss_payloads:
            # Should accept the payload (business requirement: store user input)
            response = await test_client.post("/todos", json={"text": payload})
            assert response.status_code == 201, f"Failed to store payload: {payload}"

            # Retrieve the todo and verify it's stored as literal text
            todo_id = response.json()["id"]
            get_response = await test_client.get(f"/todos/{todo_id}")
            assert get_response.status_code == 200

            stored_text = get_response.json()["text"]
            # Text should be stored exactly as provided (no modification)
            assert stored_text == payload, f"Payload was modified during storage: {payload}"

    @pytest.mark.asyncio
    async def test_response_has_xss_protection_headers(self, test_client: AsyncClient):
        """Test that responses include XSS protection headers."""
        response = await test_client.get("/todos")
        assert response.status_code == 200

        headers = response.headers

        # X-Content-Type-Options header prevents MIME type sniffing
        assert "x-content-type-options" in headers
        assert headers["x-content-type-options"] == "nosniff"

        # X-Frame-Options header prevents clickjacking
        assert "x-frame-options" in headers
        assert headers["x-frame-options"] in ["DENY", "SAMEORIGIN"]

        # Content-Security-Policy header prevents XSS
        assert "content-security-policy" in headers
        csp = headers["content-security-policy"]
        # Should restrict script sources
        assert "script-src" in csp
        assert "'unsafe-inline'" not in csp or "'strict-dynamic'" in csp

    @pytest.mark.asyncio
    async def test_content_type_enforcement(self, test_client: AsyncClient):
        """Test that content type is properly enforced."""
        response = await test_client.get("/todos")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        # Test API documentation endpoints
        docs_response = await test_client.get("/docs")
        assert docs_response.status_code == 200
        assert "text/html" in docs_response.headers["content-type"]

    @pytest.mark.asyncio
    async def test_xss_in_error_responses(self, test_client: AsyncClient):
        """Test that error responses don't reflect user input unsafely."""
        # Try to get a todo with XSS payload as ID
        xss_id = "<script>alert('xss')</script>"
        response = await test_client.get(f"/todos/{xss_id}")
        assert response.status_code in [404, 422]  # Either not found or validation error

        error_detail = response.json().get("detail", "")
        # Error message should not contain unescaped XSS payload
        if xss_id in str(error_detail):
            # If reflected, it should be properly escaped
            assert "&lt;" in str(error_detail) or "escaped" in str(error_detail).lower()

    @pytest.mark.asyncio
    async def test_html_entity_encoding_in_responses(self, test_client: AsyncClient):
        """Test that special HTML characters are properly handled."""
        special_chars_todo = "<>&\"'"
        response = await test_client.post("/todos", json={"text": special_chars_todo})
        assert response.status_code == 201

        # Retrieve and verify the content is stored as-is
        todo_id = response.json()["id"]
        get_response = await test_client.get(f"/todos/{todo_id}")
        assert get_response.status_code == 200

        stored_text = get_response.json()["text"]
        assert stored_text == special_chars_todo

    @pytest.mark.asyncio
    async def test_json_response_content_type(self, test_client: AsyncClient):
        """Test that JSON responses have correct content type."""
        endpoints = [
            "/todos",
            "/be-health",
            "/openapi.json",
        ]

        for endpoint in endpoints:
            response = await test_client.get(endpoint)
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                assert "application/json" in content_type, f"Wrong content type for {endpoint}"

    @pytest.mark.asyncio
    async def test_xss_prevention_with_unicode_payloads(self, test_client: AsyncClient):
        """Test XSS prevention with Unicode and encoded payloads."""
        unicode_payloads = [
            "\\u003cscript\\u003ealert('xss')\\u003c/script\\u003e",
            "%3Cscript%3Ealert('xss')%3C/script%3E",
            "\\x3cscript\\x3ealert('xss')\\x3c/script\\x3e",
            "＜script＞alert('xss')＜/script＞",  # Full-width characters
        ]

        for payload in unicode_payloads:
            response = await test_client.post("/todos", json={"text": payload})
            assert response.status_code == 201

            # Verify stored safely
            todo_id = response.json()["id"]
            get_response = await test_client.get(f"/todos/{todo_id}")
            assert get_response.status_code == 200
            assert get_response.json()["text"] == payload


class TestSecurityHeaders:
    """Test security headers implementation."""

    @pytest.mark.asyncio
    async def test_security_headers_on_all_endpoints(self, test_client: AsyncClient):
        """Test that security headers are present on all endpoints."""
        endpoints = [
            "/todos",
            "/be-health",
            "/docs",
            "/openapi.json",
        ]

        required_headers = {
            "x-content-type-options": "nosniff",
            "x-frame-options": ["DENY", "SAMEORIGIN"],
        }

        for endpoint in endpoints:
            response = await test_client.get(endpoint)
            if response.status_code == 200:
                for header_name, expected_values in required_headers.items():
                    assert header_name in response.headers, f"Missing {header_name} on {endpoint}"

                    header_value = response.headers[header_name]
                    if isinstance(expected_values, list):
                        assert header_value in expected_values, f"Invalid {header_name} on {endpoint}"
                    else:
                        assert header_value == expected_values, f"Invalid {header_name} on {endpoint}"

    @pytest.mark.asyncio
    async def test_csp_header_configuration(self, test_client: AsyncClient):
        """Test Content Security Policy header configuration."""
        response = await test_client.get("/todos")
        assert response.status_code == 200

        csp_header = response.headers.get("content-security-policy")
        assert csp_header is not None, "CSP header missing"

        # Basic CSP requirements for API
        assert "default-src" in csp_header
        assert "script-src" in csp_header

        # Should not allow unsafe inline scripts without strict-dynamic
        if "'unsafe-inline'" in csp_header:
            assert "'strict-dynamic'" in csp_header, "unsafe-inline without strict-dynamic"

    @pytest.mark.asyncio
    async def test_referrer_policy_header(self, test_client: AsyncClient):
        """Test Referrer Policy header for privacy protection."""
        response = await test_client.get("/todos")
        assert response.status_code == 200

        # Referrer Policy should be present for privacy
        referrer_policy = response.headers.get("referrer-policy")
        if referrer_policy:
            valid_policies = [
                "no-referrer",
                "no-referrer-when-downgrade",
                "origin",
                "origin-when-cross-origin",
                "same-origin",
                "strict-origin",
                "strict-origin-when-cross-origin",
            ]
            assert referrer_policy in valid_policies

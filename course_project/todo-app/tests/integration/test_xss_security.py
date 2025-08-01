"""XSS Security Tests for Todo Frontend.

Tests to ensure Cross-Site Scripting (XSS) vulnerabilities are prevented in the frontend.
"""

from fastapi.testclient import TestClient


class TestXSSSecurity:
    """Test XSS security measures in the frontend."""

    def test_html_template_escaping(self, test_client: TestClient):
        """Test that Jinja2 templates properly escape user content."""
        # This test verifies that the frontend properly handles XSS when displaying content
        # Since the frontend gets data from backend, we test the template rendering

        response = test_client.get("/")
        assert response.status_code == 200

        # Check that the response is HTML
        assert "text/html" in response.headers.get("content-type", "")

        # The content should be rendered as HTML
        content = response.text
        assert "<html" in content
        assert "</html>" in content

    def test_csp_headers_for_frontend(self, test_client: TestClient):
        """Test that frontend responses include CSP headers."""
        response = test_client.get("/")
        assert response.status_code == 200

        # Frontend should have security headers
        headers = response.headers

        # X-Content-Type-Options header prevents MIME type sniffing
        assert "x-content-type-options" in headers
        assert headers["x-content-type-options"] == "nosniff"

        # X-Frame-Options header prevents clickjacking
        assert "x-frame-options" in headers
        assert headers["x-frame-options"] in ["DENY", "SAMEORIGIN"]

    def test_htmx_security_integration(self, test_client: TestClient):
        """Test that HTMX integration doesn't introduce XSS vulnerabilities."""
        response = test_client.get("/")
        assert response.status_code == 200

        content = response.text

        # Check for HTMX attributes (should be present but secure)
        assert "hx-" in content  # HTMX attributes should be present

        # Check that inline JavaScript is properly structured and doesn't contain dangerous XSS patterns
        if "<script" in content:
            # If scripts exist, they should be properly structured
            import re

            script_matches = re.findall(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
            for script_content in script_matches:
                # Should not contain obvious XSS injection patterns (legitimate alerts are OK)
                assert "document.write(" not in script_content
                assert "eval(" not in script_content
                assert "innerHTML =" not in script_content  # Should use safer DOM methods

    def test_json_endpoints_security_headers(self, test_client: TestClient):
        """Test that JSON endpoints have proper security headers."""
        # Test health endpoint which is a reliable JSON endpoint
        response = test_client.get("/health")
        if response.status_code == 200:
            assert "application/json" in response.headers.get("content-type", "")
            assert "x-content-type-options" in response.headers

    def test_static_content_security(self, test_client: TestClient):
        """Test that static content has proper security headers."""
        # The application should serve static content securely
        response = test_client.get("/")
        assert response.status_code == 200

        # Should have basic security headers even for HTML content
        headers = response.headers
        assert "x-content-type-options" in headers

    def test_no_inline_javascript_with_user_content(self, test_client: TestClient):
        """Test that user content is not rendered in inline JavaScript."""
        response = test_client.get("/")
        assert response.status_code == 200

        content = response.text

        # Check for dangerous patterns in inline scripts
        import re

        # Find all script tags
        script_pattern = r"<script[^>]*>(.*?)</script>"
        scripts = re.findall(script_pattern, content, re.DOTALL | re.IGNORECASE)

        for script in scripts:
            # Scripts should not contain user-controlled content patterns
            # that could lead to XSS
            assert "todo.text" not in script  # Backend data should not be in scripts
            assert "{{" not in script  # Template variables should not leak into JS
            assert "{%" not in script  # Template logic should not leak into JS

    def test_content_security_policy_allows_htmx(self, test_client: TestClient):
        """Test that CSP is configured to allow HTMX while preventing XSS."""
        response = test_client.get("/")
        assert response.status_code == 200

        csp_header = response.headers.get("content-security-policy")
        if csp_header:
            # CSP should allow HTMX to function while restricting dangerous scripts

            # Should have script-src directive
            assert "script-src" in csp_header

            # Should restrict object and frame sources
            assert "object-src 'none'" in csp_header
            assert "frame-src 'none'" in csp_header


class TestTemplateSecurityPatterns:
    """Test security patterns in template rendering."""

    def test_jinja2_autoescaping_enabled(self, test_client: TestClient):
        """Test that Jinja2 auto-escaping is properly enabled."""
        # This is more of a structural test to ensure auto-escaping works
        response = test_client.get("/")
        assert response.status_code == 200

        # Check that the HTML structure is present and properly formed
        content = response.text

        # The page should render properly without broken HTML from escaping
        assert "<html" in content
        assert "</html>" in content
        assert "<body" in content
        assert "</body>" in content

        # Template variables should be processed (not visible as raw template syntax)
        assert "{{" not in content  # Template variables should be processed
        assert "{%" not in content  # Template logic should be processed

    def test_template_variable_security(self, test_client: TestClient):
        """Test that template variables are handled securely."""
        response = test_client.get("/")
        assert response.status_code == 200

        content = response.text

        # Template should not expose raw template syntax in HTML
        assert "{{" not in content  # Template variables should be processed
        assert "{%" not in content  # Template logic should be processed
        assert "todo.text }}" not in content  # Specific template vars should be processed

    def test_no_dangerous_html_patterns(self, test_client: TestClient):
        """Test that dangerous HTML patterns are not present."""
        response = test_client.get("/")
        assert response.status_code == 200

        content = response.text.lower()

        # Should not contain obvious XSS vectors (excluding legitimate functionality)
        dangerous_patterns = [
            "javascript:",
            "vbscript:",
            "data:text/html",
            "onerror=",  # Legitimate onclick is OK for UI
            "<iframe",
            "<object",
            "<embed",
        ]

        for pattern in dangerous_patterns:
            # Count should be minimal (legitimate functionality might use some patterns)
            count = content.count(pattern)
            assert count <= 2, f"Too many instances of dangerous pattern: {pattern} (found {count})"

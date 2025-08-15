"""
Integration tests for routing architecture and data flow validation.

CRITICAL: These tests prevent routing configuration bugs where gateway/ingress
routes browser form submissions directly to the backend, bypassing the frontend's
form-to-JSON conversion step.

The architectural constraint being tested:
- Browser submits form data (application/x-www-form-urlencoded) to /todos
- Gateway/HTTPRoute MUST route /todos to frontend service (not backend)
- Frontend converts form data to JSON and calls backend internally
- Backend expects only JSON, never raw form data

If /todos is routed directly to backend:
- Backend receives form bytes like b'text=Hello'
- Backend tries to parse as JSON and fails with 500 error
- User sees "Internal Server Error" instead of todo creation

This was the root cause of a production bug during DNS/Gateway API migration.
"""

from pathlib import Path

import pytest
import yaml


class TestRoutingArchitecture:
    """Test that routing configuration follows the required data flow architecture."""

    @pytest.fixture
    def project_root(self):
        """Get the course project root directory."""
        return Path(__file__).parent.parent.parent.parent

    def test_httproute_routes_todos_to_frontend_not_backend(self, project_root):
        """
        Test that HTTPRoute configurations route /todos to frontend service.

        WHY: This prevents the specific bug where /todos was routed directly
        to backend during DNS migration, causing form submission failures.

        SYMPTOMS if broken: 500 errors when submitting todo forms, backend
        logs showing TypeError parsing form data as JSON.
        """
        httproute_path = project_root / "manifests/base/shared/httproute.yaml"

        if not httproute_path.exists():
            pytest.skip("HTTPRoute not found - may use different routing mechanism")

        with open(httproute_path) as f:
            httproute = yaml.safe_load(f)

        # Find all /todos route rules
        todos_rules = []
        for rule in httproute["spec"]["rules"]:
            for match in rule["matches"]:
                path_value = match.get("path", {}).get("value", "")
                if path_value.endswith("/todos") or path_value == "/todos":
                    todos_rules.append(rule)

        assert todos_rules, "HTTPRoute must have rules matching /todos path"

        # Verify all /todos rules route to frontend services
        for rule in todos_rules:
            backend_refs = rule["backendRefs"]
            assert len(backend_refs) >= 1, "Each /todos rule should have at least one backend"

            for backend_ref in backend_refs:
                service_name = backend_ref["name"]
                assert "fe" in service_name or "frontend" in service_name, (
                    f"/todos routes to '{service_name}' which appears to be a backend service. "
                    f"This will bypass frontend's form-to-JSON conversion and cause 500 errors. "
                    f"Route /todos to frontend service instead."
                )

    def test_feature_overlay_todos_routing_regression(self, project_root):
        """
        Test that feature overlay doesn't route /todos directly to backend.

        WHY: This is a regression test for the specific bug we fixed where
        the feature overlay incorrectly routed /todos to backend service
        during hostname-based routing migration.

        CRITICAL: If this test fails, form submissions will fail in deployed
        feature branches with 500 Internal Server Error.
        """
        feature_kustomization = project_root / "manifests/overlays/feature/kustomization.yaml"

        if not feature_kustomization.exists():
            pytest.skip("Feature overlay not found")

        with open(feature_kustomization) as f:
            kustomization = yaml.safe_load(f)

        # Find HTTPRoute patches
        httproute_patches = [
            patch for patch in kustomization.get("patches", []) if patch.get("target", {}).get("kind") == "HTTPRoute"
        ]

        if not httproute_patches:
            pytest.skip("No HTTPRoute patches in feature overlay")

        # Check each patch for /todos routing
        for patch in httproute_patches:
            patch_content = yaml.safe_load(patch["patch"])

            # Look for rules replacement operations
            for operation in patch_content:
                if operation.get("op") == "replace" and operation.get("path") == "/spec/rules":
                    rules = operation["value"]

                    # Check each rule for /todos routing
                    for rule in rules:
                        for match in rule.get("matches", []):
                            if match.get("path", {}).get("value") == "/todos":
                                backend_refs = rule["backendRefs"]

                                for backend_ref in backend_refs:
                                    service_name = backend_ref["name"]
                                    assert "fe" in service_name or "frontend" in service_name, (
                                        f"Feature overlay routes /todos to '{service_name}' (backend service). "
                                        f"This was the root cause of form submission failures! "
                                        f"Must route to frontend service for form-to-JSON conversion."
                                    )

    def test_all_overlays_route_todos_correctly(self, project_root):
        """
        Test that no overlay accidentally routes /todos to backend services.

        WHY: Prevents regression of the routing bug across all environments.
        Any overlay routing /todos to backend will break form submissions.
        """
        overlays_dir = project_root / "manifests/overlays"

        if not overlays_dir.exists():
            pytest.skip("No overlays directory found")

        violations = []

        for overlay_dir in overlays_dir.iterdir():
            if not overlay_dir.is_dir():
                continue

            kustomization_path = overlay_dir / "kustomization.yaml"
            if not kustomization_path.exists():
                continue

            with open(kustomization_path) as f:
                kustomization = yaml.safe_load(f)

            # Check HTTPRoute patches in this overlay
            for patch in kustomization.get("patches", []):
                if patch.get("target", {}).get("kind") == "HTTPRoute":
                    patch_content = yaml.safe_load(patch["patch"])

                    # Check for /todos routing to backend
                    for operation in patch_content:
                        if operation.get("op") == "replace" and operation.get("path") == "/spec/rules":
                            rules = operation["value"]

                            for rule in rules:
                                for match in rule.get("matches", []):
                                    if match.get("path", {}).get("value") == "/todos":
                                        backend_refs = rule["backendRefs"]

                                        for backend_ref in backend_refs:
                                            service_name = backend_ref["name"]
                                            if ("be" in service_name or "backend" in service_name) and not (
                                                "fe" in service_name or "frontend" in service_name
                                            ):
                                                violations.append(
                                                    f"{overlay_dir.name}: routes /todos to {service_name}"
                                                )

        assert not violations, (
            f"Found overlays routing /todos directly to backend: {violations}. "
            f"This will cause form submission failures because backend expects JSON, not form data. "
            f"All /todos routes must go to frontend services for proper data conversion."
        )


class TestDataFlowContract:
    """Test that the data flow contract between frontend and backend is maintained."""

    @pytest.fixture
    def project_root(self):
        """Get the course project root directory."""
        return Path(__file__).parent.parent.parent.parent

    def test_backend_expects_json_input(self, project_root):
        """
        Test that backend API expects JSON input for todo creation.

        WHY: Validates that the backend contract hasn't changed. If backend
        starts accepting form data directly, the routing architecture constraint
        becomes less critical, but this should be an intentional design decision.
        """
        backend_test_file = project_root / "todo-backend/tests/integration/test_todo_endpoints.py"

        if not backend_test_file.exists():
            pytest.skip("Backend integration tests not found")

        with open(backend_test_file) as f:
            test_content = f.read()

        # Backend tests should use json= parameter for POST requests
        assert 'json={"text"' in test_content, (
            "Backend tests must use json= parameter for POST /todos, confirming JSON input expectation. "
            "If this changes, review the routing architecture requirements."
        )

        # Backend should not have tests using form data
        assert 'data={"text"' not in test_content, (
            "Backend tests should not use data= parameter (form data). "
            "Backend is designed to receive JSON from frontend, not direct form submissions."
        )

    def test_frontend_provides_form_to_json_conversion(self, project_root):
        """
        Test that frontend contains the form-to-JSON conversion logic.

        WHY: This validates that the conversion step exists in the data flow.
        Without this, the routing architecture breaks down.
        """
        frontend_routes = project_root / "todo-app/src/api/routes/todos.py"

        if not frontend_routes.exists():
            pytest.skip("Frontend todo routes not found")

        with open(frontend_routes) as f:
            routes_content = f.read()

        # Frontend must accept form input
        assert "Form(" in routes_content, (
            "Frontend todos route must accept Form input for browser submissions. "
            "This is the first step in the form-to-JSON conversion pipeline."
        )

        # Frontend must call backend client
        assert "TodoBackendClient" in routes_content, (
            "Frontend must use TodoBackendClient to forward converted data to backend. "
            "This completes the form-to-JSON conversion pipeline."
        )

    def test_todo_backend_client_sends_json(self, project_root):
        """
        Test that TodoBackendClient sends JSON to backend.

        WHY: This validates the final step in the form-to-JSON conversion.
        """
        client_file = project_root / "todo-app/src/services/todo_backend_client.py"

        if not client_file.exists():
            pytest.skip("TodoBackendClient not found")

        with open(client_file) as f:
            client_content = f.read()

        # Client must send JSON to backend
        assert 'json={"text": text}' in client_content, (
            "TodoBackendClient.create_todo must send JSON to backend. "
            "This completes the form-to-JSON conversion: "
            "Browser form -> Frontend -> JSON -> Backend."
        )

    def test_frontend_backend_data_flow_integration(self, project_root):
        """
        Integration test: verify complete data flow from form input to JSON output.

        WHY: This test ensures all pieces work together to maintain the
        architectural constraint that backend only receives JSON.
        """
        # This test could be expanded to actually test the HTTP flow,
        # but for now we validate that all components are present

        frontend_routes = project_root / "todo-app/src/api/routes/todos.py"
        backend_client = project_root / "todo-app/src/services/todo_backend_client.py"
        backend_routes = project_root / "todo-backend/src/api/routes/todos.py"

        # All components must exist
        assert frontend_routes.exists(), "Frontend routes must exist"
        assert backend_client.exists(), "Backend client must exist"
        assert backend_routes.exists(), "Backend routes must exist"

        # Frontend accepts form data
        with open(frontend_routes) as f:
            frontend_content = f.read()
        assert "Form(" in frontend_content, "Frontend must accept form data"

        # Client converts to JSON
        with open(backend_client) as f:
            client_content = f.read()
        assert "json=" in client_content, "Client must send JSON"

        # Backend expects structured data
        with open(backend_routes) as f:
            backend_content = f.read()
        # Backend should use Pydantic models, not raw form parsing
        assert "TodoCreate" in backend_content, "Backend must use structured data models"

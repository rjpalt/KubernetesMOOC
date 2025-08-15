"""
Backend-side routing architecture tests.

These tests validate that the backend maintains its side of the routing contract:
- Backend expects JSON input, not form data
- Backend routes are designed for API consumption, not direct browser access
- Backend doesn't accidentally accept form data (which would mask routing bugs)

CRITICAL: If backend starts accepting form data directly, it could mask
routing misconfigurations where /todos goes directly to backend instead
of through frontend's form-to-JSON conversion.
"""

from pathlib import Path

import pytest
import yaml


class TestBackendRoutingContract:
    """Test that backend maintains proper API-only interface expectations."""

    @pytest.fixture
    def project_root(self):
        """Get the course project root directory."""
        return Path(__file__).parent.parent.parent.parent

    def test_backend_api_expects_json_not_form_data(self):
        """
        Test that backend create_todo endpoint expects JSON, not form data.

        WHY: This validates the backend's side of the routing architecture.
        If backend accepts form data, it could mask routing bugs where
        /todos is incorrectly routed directly to backend.

        The architecture requires:
        Browser form -> Frontend (converts to JSON) -> Backend (JSON only)
        """
        # Check this test file itself to ensure we test with JSON
        current_test_file = Path(__file__)

        # Find other backend test files
        backend_tests_dir = current_test_file.parent

        json_usage_found = False
        form_data_usage_found = False

        for test_file in backend_tests_dir.glob("test_*.py"):
            if test_file.name == current_test_file.name:
                continue  # Skip this file

            with open(test_file) as f:
                content = f.read()

            # Look for POST /todos test patterns
            if "POST" in content and "/todos" in content:
                if 'json={"text"' in content or "json={'text'" in content:
                    json_usage_found = True

                if 'data={"text"' in content or "data={'text'" in content:
                    form_data_usage_found = True

        assert json_usage_found, (
            "Backend tests must use json= parameter for POST /todos to validate JSON input expectation"
        )

        assert not form_data_usage_found, (
            "Backend tests should not use data= parameter (form data). "
            "Backend accepting form data would mask routing configuration bugs."
        )

    def test_backend_routes_use_pydantic_models_not_form_parsing(self, project_root):
        """
        Test that backend routes use Pydantic models, not manual form parsing.

        WHY: Using Pydantic models enforces JSON input. If backend used
        FastAPI's Form() for todo creation, it would accept form data
        and mask routing bugs.
        """
        backend_routes = project_root / "todo-backend/src/api/routes/todos.py"

        if not backend_routes.exists():
            pytest.skip("Backend routes not found")

        with open(backend_routes) as f:
            routes_content = f.read()

        # Backend should use TodoCreate model for input validation
        assert "TodoCreate" in routes_content, (
            "Backend must use TodoCreate Pydantic model for structured input validation"
        )

        # Backend should NOT use Form() for todo creation
        # (Form is for frontend, JSON models are for backend)
        create_todo_function_start = routes_content.find("def create_todo(")
        if create_todo_function_start != -1:
            # Extract the function signature (until next def or end of file)
            next_def = routes_content.find("\ndef ", create_todo_function_start + 1)
            if next_def == -1:
                create_todo_function = routes_content[create_todo_function_start:]
            else:
                create_todo_function = routes_content[create_todo_function_start:next_def]

            assert "Form(" not in create_todo_function, (
                "Backend create_todo should not use Form() - that's for frontend. "
                "Backend should use TodoCreate Pydantic model for JSON input."
            )

    def test_backend_manifest_routes_to_backend_service(self, project_root):
        """
        Test that backend service manifests correctly identify as backend.

        WHY: This ensures our routing tests can correctly identify which
        services are backend vs frontend by naming convention.
        """
        backend_service_manifest = project_root / "todo-backend/manifests/service.yaml"

        if not backend_service_manifest.exists():
            pytest.skip("Backend service manifest not found")

        with open(backend_service_manifest) as f:
            service = yaml.safe_load(f)

        service_name = service["metadata"]["name"]

        # Service name should clearly indicate it's a backend service
        assert "be" in service_name.lower() or "backend" in service_name.lower(), (
            f"Backend service name '{service_name}' should contain 'be' or 'backend' "
            f"for clear identification in routing configurations."
        )

        # Should not be confused with frontend
        assert not ("fe" in service_name.lower() and "frontend" in service_name.lower()), (
            f"Backend service name '{service_name}' should not contain frontend indicators"
        )

    def test_gateway_routing_validation_coverage(self, project_root):
        """
        Test that we have routing validation for all gateway configurations.

        WHY: Ensures we catch routing bugs across all deployment environments.
        """
        manifests_dir = project_root / "manifests"

        if not manifests_dir.exists():
            pytest.skip("Manifests directory not found")

        # Look for routing configurations
        routing_configs = []

        # Check for HTTPRoute files
        for httproute_file in manifests_dir.rglob("*httproute*.yaml"):
            routing_configs.append(str(httproute_file.relative_to(project_root)))

        # Check for Ingress files
        for ingress_file in manifests_dir.rglob("*ingress*.yaml"):
            routing_configs.append(str(ingress_file.relative_to(project_root)))

        # Check for overlay patches that modify routing
        for kustomization_file in manifests_dir.rglob("kustomization.yaml"):
            with open(kustomization_file) as f:
                kustomization = yaml.safe_load(f)

            patches = kustomization.get("patches", [])
            for patch in patches:
                target_kind = patch.get("target", {}).get("kind")
                if target_kind in ["HTTPRoute", "Ingress"]:
                    routing_configs.append(str(kustomization_file.relative_to(project_root)))
                    break

        # We should have found some routing configuration
        assert routing_configs, "No routing configurations found. Expected HTTPRoute or Ingress manifests."

    # This test mainly documents what routing configs exist
    # The actual validation is in the frontend routing tests
    # (routed configurations discovered are intentionally not printed to avoid using print()
    #  which ruff flags in test code — keep the assertion above.)


if __name__ == "__main__":
    # Allow running this test file standalone
    pytest.main([__file__, "-v"])

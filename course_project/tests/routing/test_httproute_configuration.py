"""
Tests for HTTPRoute/Gateway routing configuration to prevent architectural regressions.

CRITICAL: These tests prevent a specific class of routing bugs where gateway/ingress
misconfiguration routes browser form submissions directly to the backend, bypassing
the frontend's form-to-JSON conversion step.

The architectural constraint being tested:
- Browser submits form data (application/x-www-form-urlencoded) to /todos
- Gateway/HTTPRoute MUST route /todos to frontend service (not backend)
- Frontend converts form data to JSON and calls backend internally
- Backend expects only JSON, never raw form data

If /todos is routed directly to backend:
- Backend receives form bytes like b'text=Hello'
- Backend tries to parse as JSON and fails with 500 error
- User sees "Internal Server Error" instead of todo creation

Test coverage:
1. Verify HTTPRoute configurations route /todos to frontend service
2. Validate that backend expects JSON (not form data)
3. Ensure frontend properly converts form data to JSON
"""

import os
import yaml
import pytest
from pathlib import Path


class TestHTTPRouteConfiguration:
    """Test HTTPRoute configurations to ensure proper service routing."""

    def test_base_httproute_routes_todos_to_frontend(self):
        """
        Test that base HTTPRoute configuration routes /todos to frontend service.
        
        WHY: This prevents accidental direct routing to backend which would
        bypass the frontend's form-to-JSON conversion step.
        """
        base_httproute_path = Path(__file__).parent.parent.parent / "manifests/base/shared/httproute.yaml"
        
        if not base_httproute_path.exists():
            pytest.skip("Base HTTPRoute not found - may use different routing mechanism")
        
        with open(base_httproute_path) as f:
            httproute = yaml.safe_load(f)
        
        # Find the /todos route rule
        todos_rule = None
        for rule in httproute['spec']['rules']:
            for match in rule['matches']:
                if match['path']['value'] in ['/project/todos', '/todos']:
                    todos_rule = rule
                    break
        
        assert todos_rule is not None, "HTTPRoute must have a rule matching /todos path"
        
        # Verify it routes to frontend service
        backend_refs = todos_rule['backendRefs']
        assert len(backend_refs) == 1, "Should have exactly one backend for /todos"
        
        backend_service = backend_refs[0]['name']
        assert 'fe' in backend_service or 'frontend' in backend_service, \
            f"/todos must route to frontend service, not {backend_service}. " \
            f"Routing to backend would bypass form-to-JSON conversion."

    def test_feature_overlay_routes_todos_to_frontend(self):
        """
        Test that feature overlay HTTPRoute correctly routes /todos to frontend.
        
        WHY: Feature overlay uses hostname-based routing instead of path prefixes.
        This test caught the bug where /todos was incorrectly routed to backend
        during the DNS migration, causing form submission failures.
        """
        feature_kustomization_path = Path(__file__).parent.parent.parent / "manifests/overlays/feature/kustomization.yaml"
        
        if not feature_kustomization_path.exists():
            pytest.skip("Feature overlay not found")
        
        with open(feature_kustomization_path) as f:
            kustomization = yaml.safe_load(f)
        
        # Find HTTPRoute patch
        httproute_patch = None
        for patch in kustomization.get('patches', []):
            if patch.get('target', {}).get('kind') == 'HTTPRoute':
                httproute_patch = patch
                break
        
        assert httproute_patch is not None, "Feature overlay must patch HTTPRoute"
        
        # Parse the patch to get the new rules
        patch_content = yaml.safe_load(httproute_patch['patch'])
        
        # Find the /todos rule in the replacement
        todos_rule = None
        for operation in patch_content:
            if operation['op'] == 'replace' and operation['path'] == '/spec/rules':
                rules = operation['value']
                for rule in rules:
                    for match in rule['matches']:
                        if match['path']['value'] == '/todos':
                            todos_rule = rule
                            break
        
        assert todos_rule is not None, "Feature overlay must define routing for /todos"
        
        # Verify it routes to frontend service
        backend_refs = todos_rule['backendRefs']
        assert len(backend_refs) == 1, "Should have exactly one backend for /todos"
        
        backend_service = backend_refs[0]['name']
        assert 'fe' in backend_service or 'frontend' in backend_service, \
            f"Feature overlay /todos must route to frontend service, not {backend_service}. " \
            f"This was the root cause of the form submission bug."

    def test_no_overlay_routes_todos_directly_to_backend(self):
        """
        Test that no overlay accidentally routes /todos directly to backend.
        
        WHY: This is a regression test for the specific bug we just fixed.
        Any overlay that routes /todos to backend will break form submissions.
        """
        overlays_dir = Path(__file__).parent.parent.parent / "manifests/overlays"
        
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
            
            # Check HTTPRoute patches
            for patch in kustomization.get('patches', []):
                if patch.get('target', {}).get('kind') == 'HTTPRoute':
                    patch_content = yaml.safe_load(patch['patch'])
                    
                    # Check for /todos routing to backend
                    for operation in patch_content:
                        if operation['op'] == 'replace' and operation['path'] == '/spec/rules':
                            rules = operation['value']
                            for rule in rules:
                                for match in rule['matches']:
                                    if match['path']['value'] == '/todos':
                                        backend_refs = rule['backendRefs']
                                        for backend_ref in backend_refs:
                                            service_name = backend_ref['name']
                                            if 'be' in service_name or 'backend' in service_name:
                                                violations.append(f"{overlay_dir.name}: routes /todos to {service_name}")
        
        assert not violations, \
            f"Found overlays routing /todos directly to backend: {violations}. " \
            f"This will cause form submission failures because backend expects JSON, not form data."


class TestDataFlowExpectations:
    """Test that services have correct data format expectations."""

    def test_backend_expects_json_for_create_todo(self):
        """
        Test that backend tests confirm JSON input expectation for POST /todos.
        
        WHY: This validates that the backend is designed to receive JSON,
        not form data. If this expectation changes, the routing architecture
        would need to be reconsidered.
        """
        # Check that backend tests use json= parameter, not data=
        backend_test_path = Path(__file__).parent.parent.parent / "todo-backend/tests/integration/test_todo_endpoints.py"
        
        if not backend_test_path.exists():
            pytest.skip("Backend tests not found")
        
        with open(backend_test_path) as f:
            test_content = f.read()
        
        # Look for POST /todos test calls
        assert 'json={"text"' in test_content, \
            "Backend tests must use json= parameter for POST /todos, confirming JSON expectation"
        
        # Ensure no form data submissions in backend tests
        assert 'data={"text"' not in test_content, \
            "Backend tests should not use data= parameter - backend expects JSON only"

    def test_frontend_has_form_to_json_conversion(self):
        """
        Test that frontend service contains form-to-JSON conversion logic.
        
        WHY: This validates that the frontend has the conversion step that
        the routing architecture depends on.
        """
        frontend_routes_path = Path(__file__).parent.parent.parent / "todo-app/src/api/routes/todos.py"
        
        if not frontend_routes_path.exists():
            pytest.skip("Frontend todo routes not found")
        
        with open(frontend_routes_path) as f:
            routes_content = f.read()
        
        # Check for form input and JSON output pattern
        assert 'Form(' in routes_content, \
            "Frontend must accept form input (application/x-www-form-urlencoded)"
        
        assert 'TodoBackendClient' in routes_content, \
            "Frontend must use TodoBackendClient to call backend with JSON"

    def test_frontend_backend_client_sends_json(self):
        """
        Test that TodoBackendClient sends JSON to backend.
        
        WHY: This validates the conversion step exists in the data flow.
        """
        client_path = Path(__file__).parent.parent.parent / "todo-app/src/services/todo_backend_client.py"
        
        if not client_path.exists():
            pytest.skip("TodoBackendClient not found")
        
        with open(client_path) as f:
            client_content = f.read()
        
        # Check that create_todo method uses json= parameter
        assert 'json={"text": text}' in client_content, \
            "TodoBackendClient must send JSON to backend, completing the form-to-JSON conversion"


if __name__ == "__main__":
    # Run tests standalone for development
    pytest.main([__file__, "-v"])

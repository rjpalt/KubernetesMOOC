"""SQL injection prevention tests for todo-backend.

Tests to validate that the backend is protected against SQL injection attacks
through malicious todo text content and parameters. These tests ensure that:

1. Malicious SQL payloads are safely stored as literal text
2. Server remains stable under SQL injection attempts  
3. Database integrity is maintained
4. SQLAlchemy ORM parameterization provides adequate protection

Following TDD principles to validate security before implementation.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient


class TestSQLInjectionPrevention:
    """Test SQL injection prevention in todo operations."""

    @pytest_asyncio.fixture(autouse=True)
    async def setup_clean_database(self, test_client: AsyncClient):
        """Ensure clean database state for each test."""
        # Get current todos
        response = await test_client.get("/todos")
        todos = response.json()
        
        # Delete all existing todos
        for todo in todos:
            await test_client.delete(f"/todos/{todo['id']}")

    async def test_sql_injection_in_todo_text_creation(self, test_client: AsyncClient):
        """Test that SQL injection payloads in todo text are safely handled."""
        malicious_inputs = [
            "'; DROP TABLE todos; --",
            "1' OR '1'='1",
            "'; DELETE FROM todos--",
            "' UNION SELECT * FROM todos--",
            "'; INSERT INTO todos (text) VALUES ('hacked'); --",
            "' OR 1=1; --",
            "admin'--",
            "admin' OR '1'='1",
            "'; UPDATE todos SET text='hacked' WHERE '1'='1'; --",
        ]

        created_todos = []
        
        for malicious_input in malicious_inputs:
            # Create todo with malicious input
            response = await test_client.post("/todos", json={"text": malicious_input})
            
            # SQLAlchemy ORM should protect us, verify:
            # 1. Request doesn't crash the server
            assert response.status_code in [201, 400, 422], f"Unexpected status for input: {malicious_input}"
            
            # 2. If accepted, data is stored safely
            if response.status_code == 201:
                created_todo = response.json()
                created_todos.append(created_todo)
                
                # Verify the malicious text is stored as-is, not executed
                todo_id = created_todo["id"]
                get_response = await test_client.get(f"/todos/{todo_id}")
                assert get_response.status_code == 200
                stored_todo = get_response.json()
                assert stored_todo["text"] == malicious_input, f"Text mismatch for: {malicious_input}"

        # Verify database integrity - only expected todos exist
        all_todos_response = await test_client.get("/todos")
        assert all_todos_response.status_code == 200
        all_todos = all_todos_response.json()
        
        # Should only have the todos we created (none injected by malicious SQL)
        assert len(all_todos) == len(created_todos), "Unexpected number of todos - possible SQL injection"

    async def test_sql_injection_in_todo_id_parameters(self, test_client: AsyncClient):
        """Test that SQL injection in ID parameters is safely handled."""
        # First create a legitimate todo
        create_response = await test_client.post("/todos", json={"text": "Legitimate todo"})
        assert create_response.status_code == 201
        legitimate_todo = create_response.json()
        legitimate_id = legitimate_todo["id"]

        malicious_ids = [
            "1'; DROP TABLE todos; --",
            "1 OR 1=1",
            "1; DELETE FROM todos",
            "1 UNION SELECT * FROM todos",
            "'; UPDATE todos SET text='hacked' WHERE id='1",
            "1' OR '1'='1' --",
        ]

        for malicious_id in malicious_ids:
            # Test GET with malicious ID
            get_response = await test_client.get(f"/todos/{malicious_id}")
            # Should return 404 for non-existent/malformed ID, not crash
            assert get_response.status_code in [404, 422], f"Unexpected status for malicious ID: {malicious_id}"

            # Test PUT with malicious ID  
            put_response = await test_client.put(f"/todos/{malicious_id}", json={"text": "Updated text"})
            assert put_response.status_code in [404, 422], f"PUT should fail for malicious ID: {malicious_id}"

            # Test DELETE with malicious ID
            delete_response = await test_client.delete(f"/todos/{malicious_id}")
            assert delete_response.status_code in [404, 422], f"DELETE should fail for malicious ID: {malicious_id}"

        # Verify legitimate todo still exists and is unchanged
        final_check = await test_client.get(f"/todos/{legitimate_id}")
        assert final_check.status_code == 200
        final_todo = final_check.json()
        assert final_todo["text"] == "Legitimate todo", "Legitimate todo was modified by SQL injection attempt"

    async def test_sql_injection_in_todo_updates(self, test_client: AsyncClient):
        """Test that SQL injection in update operations is safely handled."""
        # Create a todo to update
        create_response = await test_client.post("/todos", json={"text": "Original text"})
        assert create_response.status_code == 201
        todo = create_response.json()
        todo_id = todo["id"]

        malicious_update_texts = [
            "Updated'; DROP TABLE todos; --",
            "Updated' OR '1'='1",
            "Updated'; DELETE FROM todos WHERE '1'='1'; --",
            "Updated' UNION SELECT password FROM users --",
        ]

        for malicious_text in malicious_update_texts:
            # Update with malicious text
            response = await test_client.put(f"/todos/{todo_id}", json={"text": malicious_text})
            
            # Should either succeed (storing safely) or reject with validation error
            assert response.status_code in [200, 400, 422], f"Unexpected status for update: {malicious_text}"
            
            if response.status_code == 200:
                # Verify the malicious text is stored safely
                get_response = await test_client.get(f"/todos/{todo_id}")
                assert get_response.status_code == 200
                updated_todo = get_response.json()
                assert updated_todo["text"] == malicious_text, f"Update text mismatch: {malicious_text}"

        # Verify database integrity
        all_todos_response = await test_client.get("/todos")
        assert all_todos_response.status_code == 200
        all_todos = all_todos_response.json()
        
        # Should only have our test todo
        assert len(all_todos) == 1, "Database corruption detected - unexpected number of todos"

    async def test_database_stability_under_injection_attacks(self, test_client: AsyncClient):
        """Test that database remains stable under sustained SQL injection attempts."""
        # Create baseline data
        baseline_response = await test_client.post("/todos", json={"text": "Baseline todo"})
        assert baseline_response.status_code == 201
        baseline_todo = baseline_response.json()

        # Launch multiple injection attempts
        injection_payloads = [
            "'; DROP DATABASE todo_test; --",
            "'; TRUNCATE TABLE todos; --", 
            "'; ALTER TABLE todos DROP COLUMN text; --",
            "admin'; DROP TABLE todos; SELECT * FROM todos WHERE 't'='t",
            "1'; DELETE FROM todos; INSERT INTO todos (text) VALUES ('mass_injection'); --",
        ]

        for payload in injection_payloads:
            # Try creating todos with dangerous payloads
            create_response = await test_client.post("/todos", json={"text": payload})
            assert create_response.status_code in [201, 400, 422], f"Server crashed on payload: {payload}"

            # Try updating with dangerous payloads
            if baseline_todo:
                update_response = await test_client.put(f"/todos/{baseline_todo['id']}", json={"text": payload})
                assert update_response.status_code in [200, 400, 422], f"Server crashed on update: {payload}"

        # Verify baseline todo still exists (database not corrupted)
        check_response = await test_client.get(f"/todos/{baseline_todo['id']}")
        assert check_response.status_code == 200, "Baseline todo lost - database may be corrupted"

        # Verify database is still functional
        health_response = await test_client.get("/be-health")
        assert health_response.status_code == 200, "Database health check failed after injection attempts"

    async def test_parameter_types_prevent_injection(self, test_client: AsyncClient):
        """Test that proper parameter typing prevents injection in ID fields."""
        # Test non-numeric ID values (should be rejected before reaching SQL)
        non_numeric_ids = [
            "abc",
            "1.5", 
            "1e10",
            "null",
            "undefined",
            "'1'",
            '"1"',
        ]

        for invalid_id in non_numeric_ids:
            get_response = await test_client.get(f"/todos/{invalid_id}")
            # Should fail with 404/422, not reach SQL layer
            assert get_response.status_code in [404, 422], f"Non-numeric ID should be rejected: {invalid_id}"

            put_response = await test_client.put(f"/todos/{invalid_id}", json={"text": "test"})
            assert put_response.status_code in [404, 422], f"Non-numeric ID should be rejected in PUT: {invalid_id}"

            delete_response = await test_client.delete(f"/todos/{invalid_id}")
            assert delete_response.status_code in [404, 422], f"Non-numeric ID should be rejected in DELETE: {invalid_id}"

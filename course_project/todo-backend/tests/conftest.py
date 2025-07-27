"""Backend test configuration and shared fixtures.

This conftest.py provides:
- Database lifecycle management (starts containers if needed)
- FastAPI test client for backend API testing
- Database test fixtures with clean isolation
- Shared fixtures for backend testing
- Test configuration for the modular backend architecture
"""

import os
import subprocess
import time
import asyncio
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.main import create_app
from src.database.connection import db_manager, DatabaseManager
from src.database.models import Base


# Set test environment variables
os.environ["DATABASE_URL"] = "postgresql+asyncpg://todouser:todopass@localhost:5433/todoapp_test"


def ensure_test_database_running():
    """Ensure the test database container is running.
    
    This function demonstrates container lifecycle management patterns
    that are essential for Kubernetes testing scenarios.
    """
    try:
        # Check if test database is accessible
        result = subprocess.run(
            ["docker", "exec", "todo_postgres_test", "pg_isready", "-U", "todouser", "-d", "todoapp_test"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ Test database already running")
            return
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        pass

    print("🚀 Starting test database container...")
    
    # Start the database containers
    try:
        subprocess.run(
            ["docker-compose", "-f", "docker-compose.dev.yml", "up", "-d", "postgres_test"],
            cwd=os.path.dirname(os.path.dirname(__file__)),  # Go to todo-backend root
            check=True,
            capture_output=True
        )
        
        # Wait for database to be ready (with timeout)
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                result = subprocess.run(
                    ["docker", "exec", "todo_postgres_test", "pg_isready", "-U", "todouser", "-d", "todoapp_test"],
                    capture_output=True,
                    timeout=2
                )
                if result.returncode == 0:
                    print(f"✅ Test database ready after {attempt + 1} attempts")
                    time.sleep(1)  # Give it one more second to be fully ready
                    return
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                pass
            time.sleep(1)
        
        raise RuntimeError("Test database failed to start within 30 seconds")
        
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to start test database: {e}")


# Ensure database is running at session start
def pytest_sessionstart(session):
    """Called after the Session object has been created."""
    ensure_test_database_running()


@pytest_asyncio.fixture(scope="function")
async def test_db_engine():
    """Create test database engine for each test.
    
    Function-scoped engine to avoid event loop issues.
    Each test gets a completely fresh engine and connection pool.
    """
    engine = create_async_engine(
        "postgresql+asyncpg://todouser:todopass@localhost:5433/todoapp_test",
        echo=False,
        # Minimal pooling for test isolation
        pool_size=1,
        max_overflow=0,
        pool_timeout=10,
        pool_pre_ping=False,  # Disable ping to avoid loop issues
        pool_recycle=-1       # Disable connection recycling
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db_manager(test_db_engine):
    """Test database manager with clean state.
    
    This fixture demonstrates proper dependency injection
    for testing database-backed services in containers.
    Each test gets a completely fresh database schema.
    """
    # Store the original global db_manager
    import src.database.connection
    import src.database.operations
    original_manager = src.database.connection.db_manager
    
    # Create a test database manager with our test engine
    test_manager = DatabaseManager()
    test_manager.engine = test_db_engine
    test_manager.session_factory = async_sessionmaker(
        bind=test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # Replace global db_manager in all modules that import it
    src.database.connection.db_manager = test_manager
    src.database.operations.db_manager = test_manager
    
    # Create fresh tables for this test (simplified approach)
    async with test_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield test_manager
    
    # Restore original manager in all modules (cleanup happens with engine disposal)
    src.database.connection.db_manager = original_manager
    src.database.operations.db_manager = original_manager


@pytest.fixture
def test_client(test_db_manager):
    """Create a FastAPI test client for backend API testing.

    This fixture provides a test client that:
    - Uses the backend's FastAPI app with test database
    - Doesn't require running the actual server
    - Handles async endpoints automatically  
    - Provides HTTP interface testing
    
    Important for Kubernetes testing: The test_db_manager fixture already
    replaces the global db_manager, so TodoService will automatically use
    the test database.
    """
    app = create_app()
    return TestClient(app)


@pytest_asyncio.fixture
async def async_test_client(test_db_manager):
    """Create an async HTTP client for testing async endpoints.
    
    This fixture is useful for:
    - Full async testing workflows
    - Testing WebSocket connections
    - Advanced HTTP client features
    """
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_todo_data():
    """Sample todo data matching backend's Todo model format.

    This ensures test data matches what the backend actually returns,
    which is crucial for microservice contract consistency.
    """
    return {
        "text": "Learn Kubernetes testing patterns",
        "status": "not-done",  # Note: hyphen, not underscore!
    }


@pytest.fixture
def sample_todos_list():
    """Sample list of todos for testing list endpoints."""
    return [
        {
            "text": "Learn Kubernetes testing patterns",
            "status": "not-done",
        },
        {
            "text": "Understand microservice testing",
            "status": "done",
        },
    ]

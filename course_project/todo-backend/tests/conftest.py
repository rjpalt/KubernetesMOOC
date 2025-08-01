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

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database.connection import DatabaseManager
from src.database.models import Base
from src.main import create_app


def _configure_test_database():
    """Configure test database based on environment.

    This demonstrates environment-specific configuration patterns
    that are essential in Kubernetes deployments where different
    environments (dev, staging, prod) use different credentials.
    """
    # Check if running in CI/CD environment (GitHub Actions or act)
    is_ci = os.getenv("GITHUB_ACTIONS") == "true" or os.getenv("ACT") == "true"

    # Additional check for ACT-specific environment variables
    has_ci_vars = bool(os.getenv("postgres_user")) and bool(os.getenv("postgres_password"))

    if is_ci and has_ci_vars:
        # CI environment: use environment variables from secrets
        postgres_user = os.getenv("postgres_user", "test_user")
        postgres_password = os.getenv("postgres_password", "test_password123")
        postgres_host = os.getenv("postgres_host", "localhost")
        postgres_port = os.getenv("postgres_port", "5433")
        postgres_db = os.getenv("postgres_db", "test_todoapp")

        database_url = (
            f"postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
        )
        os.environ["DATABASE_URL"] = database_url

        # Set individual environment variables for compatibility
        os.environ["POSTGRES_USER"] = postgres_user
        os.environ["POSTGRES_PASSWORD"] = postgres_password
        os.environ["POSTGRES_HOST"] = postgres_host
        os.environ["POSTGRES_PORT"] = postgres_port
        os.environ["POSTGRES_DB"] = postgres_db
    else:
        # Local development: use local Docker credentials
        os.environ["DATABASE_URL"] = "postgresql+asyncpg://todouser:todopass@localhost:5433/todoapp_test"
        os.environ["POSTGRES_USER"] = "todouser"
        os.environ["POSTGRES_PASSWORD"] = "todopass"
        os.environ["POSTGRES_HOST"] = "localhost"
        os.environ["POSTGRES_PORT"] = "5433"
        os.environ["POSTGRES_DB"] = "todoapp_test"


# Configure database based on environment (lazy loading for CI/CD compatibility)
# _configure_test_database()  # Commented out - will be called from fixtures instead


def ensure_test_database_running():
    """Ensure the test database container is running.

    This function demonstrates container lifecycle management patterns
    that are essential for Kubernetes testing scenarios.
    """
    # Skip database container management in CI environments
    # (database is provided as a service container)
    is_ci = os.getenv("GITHUB_ACTIONS") == "true" or os.getenv("ACT") == "true"
    if is_ci:
        return

    # Get current database configuration
    postgres_user = os.getenv("POSTGRES_USER", "todouser")
    postgres_db = os.getenv("POSTGRES_DB", "todoapp_test")

    try:
        # Check if test database is accessible
        result = subprocess.run(
            ["docker", "exec", "todo_postgres_test", "pg_isready", "-U", postgres_user, "-d", postgres_db],
            capture_output=True,
            timeout=5,
        )
        if result.returncode == 0:
            return
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Start the database containers
    try:
        subprocess.run(
            ["docker-compose", "-f", "docker-compose.dev.yml", "up", "-d", "postgres_test"],
            cwd=os.path.dirname(os.path.dirname(__file__)),  # Go to todo-backend root
            check=True,
            capture_output=True,
        )

        # Wait for database to be ready (with timeout)
        max_attempts = 30
        for _attempt in range(max_attempts):
            try:
                result = subprocess.run(
                    ["docker", "exec", "todo_postgres_test", "pg_isready", "-U", "todouser", "-d", "todoapp_test"],
                    capture_output=True,
                    timeout=2,
                )
                if result.returncode == 0:
                    time.sleep(1)  # Give it one more second to be fully ready
                    return
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                pass
            time.sleep(1)

        raise RuntimeError("Test database failed to start within 30 seconds")

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to start test database: {e}") from e


# Ensure database is running at session start
def pytest_sessionstart(session):
    """Called after the Session object has been created."""
    # Skip Docker setup in CI environments (GitHub Actions provides the database service)
    if os.environ.get("GITHUB_ACTIONS") == "true":
        return

    # For local development, start Docker containers
    ensure_test_database_running()


@pytest_asyncio.fixture(scope="function")
async def test_db_engine():
    """Create test database engine for each test.

    Function-scoped engine to avoid event loop issues.
    Each test gets a completely fresh engine and connection pool.
    """
    # Configure test database based on environment (CI vs local)
    _configure_test_database()

    # Get database URL from configuration
    db_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://todouser:todopass@localhost:5433/todoapp_test")

    engine = create_async_engine(
        db_url,
        echo=False,
        # Minimal pooling for test isolation
        pool_size=1,
        max_overflow=0,
        pool_timeout=10,
        pool_pre_ping=False,  # Disable ping to avoid loop issues
        pool_recycle=-1,  # Disable connection recycling
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
    test_manager.session_factory = async_sessionmaker(bind=test_db_engine, class_=AsyncSession, expire_on_commit=False)

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


@pytest_asyncio.fixture
async def test_client(test_db_manager):
    """Create an async FastAPI test client for backend API testing.

    This fixture provides an async test client that:
    - Uses the backend's FastAPI app with test database
    - Properly handles async endpoints and database operations
    - Avoids event loop conflicts with async database operations
    - Provides HTTP interface testing compatible with async workflows

    Important for Kubernetes testing: The test_db_manager fixture already
    replaces the global db_manager, so TodoService will automatically use
    the test database.

    Using AsyncClient with httpx.ASGITransport instead of TestClient to avoid
    event loop conflicts that occur when sync TestClient tries to call async
    database operations.
    """
    from httpx import ASGITransport

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


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

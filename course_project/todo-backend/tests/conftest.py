"""Backend test configuration and shared fixtures.

This conftest.py provides:
- FastAPI test client for backend API testing
- Database test fixtures with clean isolation
- Shared fixtures for backend testing
- Test configuration for the modular backend architecture
"""

import os
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.main import create_app
from src.database.connection import db_manager, DatabaseManager
from src.database.models import Base


# Set test environment variables
os.environ["DATABASE_URL"] = "postgresql+asyncpg://todouser:todopass@localhost:5433/todoapp_test"


@pytest_asyncio.fixture(scope="session")
async def test_db_engine():
    """Create test database engine."""
    engine = create_async_engine(
        "postgresql+asyncpg://todouser:todopass@localhost:5433/todoapp_test",
        echo=False
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db_session(test_db_engine):
    """Create clean test database session for each test."""
    # Create all tables
    async with test_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    session_factory = async_sessionmaker(
        bind=test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with session_factory() as session:
        yield session
    
    # Clean up tables after test
    async with test_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def test_db_manager(test_db_engine):
    """Test database manager with clean state."""
    # Create a test database manager
    test_manager = DatabaseManager()
    test_manager.engine = test_db_engine
    test_manager.session_factory = async_sessionmaker(
        bind=test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # Create tables
    async with test_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Replace global db_manager for tests
    original_manager = db_manager
    import src.database.connection
    src.database.connection.db_manager = test_manager
    
    yield test_manager
    
    # Clean up and restore
    async with test_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    src.database.connection.db_manager = original_manager


@pytest.fixture
def test_client(test_db_manager):
    """Create a FastAPI test client for backend API testing.

    This fixture provides a test client that:
    - Uses the backend's FastAPI app with test database
    - Doesn't require running the actual server
    - Handles async endpoints automatically
    - Provides HTTP interface testing
    """
    app = create_app()
    return TestClient(app)


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

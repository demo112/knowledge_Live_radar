
import os
import pytest
import pytest_asyncio

# Set dummy embedding model for tests to prevent network calls
os.environ["EMBEDDING_MODEL"] = "dummy"

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app
from unittest.mock import patch

# 使用内存 SQLite 数据库
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(autouse=True)
async def mock_sleep():
    """Globally disable random sleep in RequestUtils for all tests."""
    async def _mock_sleep(*args, **kwargs):
        pass
        
    with patch("app.services.fetchers.request_utils.RequestUtils.random_sleep", side_effect=_mock_sleep):
        yield

@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    
    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    TestingSessionLocal = async_sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=engine, 
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with TestingSessionLocal() as session:
        yield session
        
    # 清理
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    
    app.dependency_overrides.clear()

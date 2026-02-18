import pytest
from datetime import datetime, timedelta
from app.services.ai_monitor_service import AIMonitorService
from app.models.ai_metric import AIMetric
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

@pytest.mark.asyncio
async def test_ai_monitor_service(db_session: AsyncSession):
    service = AIMonitorService(db_session)
    
    # Create some metrics
    metrics = [
        AIMetric(
            module="test",
            model="gpt-4",
            provider="cloud",
            latency=1.5,
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            status="success"
        ),
        AIMetric(
            module="test",
            model="gpt-3.5",
            provider="cloud",
            latency=0.5,
            prompt_tokens=50,
            completion_tokens=20,
            total_tokens=70,
            status="success"
        ),
        AIMetric(
            module="crawl",
            model="local-model",
            provider="local",
            latency=2.0,
            prompt_tokens=10,
            completion_tokens=10,
            total_tokens=20,
            status="error",
            error_message="Timeout"
        )
    ]
    
    db_session.add_all(metrics)
    await db_session.commit()
    
    # Test get_metrics
    items, total = await service.get_metrics()
    assert total == 3
    assert len(items) == 3
    
    # Test filtering by status
    items, total = await service.get_metrics(status="success")
    assert total == 2
    assert all(m.status == "success" for m in items)
    
    # Test filtering by provider
    items, total = await service.get_metrics(provider="local")
    assert total == 1
    assert items[0].provider == "local"
    
    # Test aggregation
    stats = await service.get_aggregated_stats()
    assert stats["total_requests"] == 3
    # 2 success out of 3
    assert abs(stats["success_rate"] - (2/3 * 100)) < 0.01
    assert stats["total_tokens"] == 150 + 70 + 20
    
    # Check model stats
    model_stats = {m["model"]: m for m in stats["models"]}
    assert "gpt-4" in model_stats
    assert model_stats["gpt-4"]["count"] == 1
    assert model_stats["gpt-4"]["success_rate"] == 100.0
    
    assert "local-model" in model_stats
    assert model_stats["local-model"]["count"] == 1
    assert model_stats["local-model"]["success_rate"] == 0.0

    # Test clean
    # Add an old metric
    old_metric = AIMetric(
        module="old",
        model="old-model",
        provider="local",
        latency=1.0,
        status="success",
        timestamp=datetime.now() - timedelta(days=31)
    )
    db_session.add(old_metric)
    await db_session.commit()
    
    count_before = await service.get_metrics()
    assert count_before[1] == 4
    
    deleted = await service.clean_old_metrics(days=30)
    assert deleted == 1
    
    count_after = await service.get_metrics()
    assert count_after[1] == 3
